from app.repository.claim_repository import ClaimRepository
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from google import genai
from google.genai import types
import io
from PIL import Image
import base64
import tempfile
import os
import time

class FactCheckService:
    def __init__(self):
        self.repo = ClaimRepository()
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def check_fact(self, claim_text: str):
        # Create chat session with Gemini model
        chat = self.client.chats.create(model=self.model)
        response = chat.send_message(f"Fact check this claim: {claim_text}")

        verdict = response.text.strip()

        # ✅ Save both prompt and response to DB
        self.repo.save(claim_text, verdict)

        # ✅ Return structured response to API
        return {
            "claim_text": claim_text,
            "response_text": verdict
        }



    def check_multimodal_fact(self, claim_text: str, file_content: bytes, content_type: str, filename: str):
        """
        Handle multimodal fact checking with images, videos, and audio
        """
        temp_file_path = None
        try:
            # Save file temporarily
            suffix = os.path.splitext(filename)[1] if filename else ''
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Determine the media type and create appropriate prompt
            if content_type and content_type.startswith("image/"):
                # Handle image
                prompt = f"Analyze this image and fact-check any claims visible in it."
                if claim_text:
                    prompt = f"Fact check this claim based on the image: {claim_text}"

            elif content_type and content_type.startswith("video/"):
                # Handle video
                prompt = f"Analyze this video and fact-check any claims visible or spoken in it."
                if claim_text:
                    prompt = f"Fact check this claim based on the video: {claim_text}"

            elif content_type and content_type.startswith("audio/"):
                # Handle audio
                prompt = f"Transcribe and fact-check any claims made in this audio."
                if claim_text:
                    prompt = f"Fact check this claim based on the audio: {claim_text}"

            else:
                return {
                    "claim_text": claim_text or "Unknown media type",
                    "verdict": f"Unsupported file type: {content_type}",
                    "evidence": []
                }

            # For image files, we can send them directly inline
            # For video/audio files, we need to upload them first
            chat = self.client.chats.create(model=self.model)

            if content_type and content_type.startswith("image/"):
                # For images, use inline Part with image data
                print(f"Processing image: {filename}")
                image = Image.open(temp_file_path)
                response = chat.send_message([prompt, image])
                print(f"Image processed successfully")

            elif content_type and (content_type.startswith("video/") or content_type.startswith("audio/")):
                # For video and audio, upload to Gemini Files API
                file_type = "video" if content_type.startswith("video/") else "audio"
                print(f"Uploading {file_type}: {filename} (content_type: {content_type})")
                print(f"File size: {len(file_content)} bytes")

                # For audio files, especially WebM from browser recordings, try converting to a compatible format
                final_file_path = temp_file_path

                if content_type and content_type.startswith("audio/"):
                    try:
                        # Try to convert WebM/other formats to WAV for better compatibility
                        from pydub import AudioSegment

                        print(f"Converting audio to WAV format for better compatibility...")
                        audio = AudioSegment.from_file(temp_file_path)

                        # Create new temp file for WAV
                        wav_path = temp_file_path.replace(os.path.splitext(temp_file_path)[1], '.wav')
                        audio.export(wav_path, format="wav")
                        final_file_path = wav_path
                        print(f"Audio converted successfully to WAV")

                    except FileNotFoundError as fnf_error:
                        error_msg = (
                            "FFmpeg is not installed or not in PATH. "
                            "Audio conversion requires FFmpeg.\n"
                            "Please install FFmpeg:\n"
                            "  Windows: See INSTALL_FFMPEG.md in the project root\n"
                            "  Quick: choco install ffmpeg (requires Chocolatey)\n"
                            "After installation, restart the server."
                        )
                        print(f"ERROR: {error_msg}")
                        raise ValueError(error_msg)
                    except Exception as conv_error:
                        print(f"Audio conversion failed: {str(conv_error)}")
                        print(f"WARNING: Using original format may not work with Gemini API")
                        # Continue with original file if conversion fails
                        final_file_path = temp_file_path

                try:
                    # The correct API signature uses 'file' keyword argument
                    uploaded_file = self.client.files.upload(file=final_file_path)
                    print(f"File uploaded successfully: {uploaded_file.name}")
                    print(f"File URI: {uploaded_file.uri}")
                    print(f"File MIME type: {uploaded_file.mime_type}")

                    # Wait for file processing to complete (both video and audio need this)
                    print(f"Waiting for {file_type} processing... Initial state: {uploaded_file.state.name}")

                    max_wait = 300  # 5 minutes max wait
                    waited = 0

                    while uploaded_file.state.name == "PROCESSING" and waited < max_wait:
                        time.sleep(2)
                        waited += 2
                        try:
                            uploaded_file = self.client.files.get(name=uploaded_file.name)
                            print(f"{file_type.capitalize()} state: {uploaded_file.state.name} (waited {waited}s)")
                        except Exception as e:
                            print(f"Error checking file state: {str(e)}")
                            break

                    if uploaded_file.state.name == "FAILED":
                        raise ValueError(f"{file_type.capitalize()} processing failed. Check if format is supported.")
                    elif uploaded_file.state.name == "PROCESSING":
                        raise ValueError(f"{file_type.capitalize()} processing timeout after {max_wait} seconds")
                    elif uploaded_file.state.name != "ACTIVE":
                        raise ValueError(f"File is in {uploaded_file.state.name} state, expected ACTIVE")

                    print(f"{file_type.capitalize()} is now ACTIVE and ready to use")

                    # Send message with the uploaded file
                    print(f"Sending message to Gemini with uploaded file...")
                    response = chat.send_message([prompt, uploaded_file])
                    print(f"Response received from Gemini")

                except Exception as upload_error:
                    print(f"Error during file upload/processing: {str(upload_error)}")
                    raise
                finally:
                    # Clean up converted WAV file if it was created
                    if final_file_path != temp_file_path and os.path.exists(final_file_path):
                        try:
                            os.unlink(final_file_path)
                        except:
                            pass
            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            verdict = response.text.strip()
            evidence = []

            claim = {
                "claim_text": claim_text or f"Media file: {filename}",
                "verdict": verdict,
                "evidence": evidence,
                "media_type": content_type
            }
            self.repo.save(claim_text or f"Media file: {filename}", verdict)
            return claim

        except Exception as e:
            return {
                "claim_text": claim_text or f"Media file: {filename}",
                "verdict": f"Error processing media: {str(e)}",
                "evidence": [],
                "error": str(e)
            }
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
