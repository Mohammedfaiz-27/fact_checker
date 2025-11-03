from app.repository.claim_repository import ClaimRepository
from app.core.config import GEMINI_API_KEY, GEMINI_MODEL
from app.services.text_extraction_service import TextExtractionService
from app.services.professional_fact_check_service import ProfessionalFactCheckService
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
        self.text_extractor = TextExtractionService()
        self.professional_service = ProfessionalFactCheckService()
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
        Handle multimodal fact checking with images, videos, and audio.

        Pipeline:
        1. Extract text from media (OCR for images, speech-to-text for video/audio)
        2. Combine with user's claim text (if provided)
        3. Pass to professional fact-checking service with Perplexity Deep Search
        """
        try:
            print(f"\n{'='*60}")
            print(f"MULTIMODAL FACT-CHECK: {filename} ({content_type})")
            print(f"User claim: {claim_text if claim_text else 'None provided'}")
            print(f"{'='*60}\n")

            # Step 1: Extract text from media
            extracted_data = None
            media_type = None

            if content_type and content_type.startswith("image/"):
                media_type = "image"
                print("📸 Extracting text from image using OCR...")
                extracted_data = self.text_extractor.extract_text_from_image(file_content, filename)

            elif content_type and content_type.startswith("video/"):
                media_type = "video"
                print("🎥 Extracting text from video (speech + visual text)...")
                extracted_data = self.text_extractor.extract_text_from_video(file_content, filename)

            elif content_type and content_type.startswith("audio/"):
                media_type = "audio"
                print("🎤 Extracting text from audio (speech-to-text)...")
                extracted_data = self.text_extractor.extract_text_from_audio(file_content, filename, content_type)

            else:
                return {
                    "claim_text": claim_text or "Unknown media type",
                    "status": "❌ Error",
                    "explanation": f"Unsupported file type: {content_type}",
                    "sources": [],
                    "media_type": content_type
                }

            # Check if extraction failed
            if extracted_data.get("error"):
                return {
                    "claim_text": claim_text or f"Media file: {filename}",
                    "status": "❌ Error",
                    "explanation": extracted_data["error"],
                    "sources": [],
                    "media_type": content_type
                }

            extracted_text = extracted_data.get("text", "")
            print(f"\n✅ Text extraction complete!")
            print(f"Extracted content (preview): {extracted_text[:200]}...\n")

            # Step 2: Combine extracted text with user's claim
            if claim_text:
                # User provided specific claim - use it as primary, extracted text as context
                combined_claim = f"{claim_text}\n\nContext from {media_type}: {extracted_text}"
                print(f"📝 Using user's claim with {media_type} context")
            else:
                # No user claim - use extracted text
                combined_claim = f"Claims from {media_type}: {extracted_text}"
                print(f"📝 Using extracted text from {media_type} as claim")

            # Step 3: Pass to professional fact-checking service (includes Perplexity Deep Search)
            print(f"\n🔍 Starting professional fact-check pipeline with Perplexity Deep Search...")
            result = self.professional_service.check_fact(combined_claim)

            # Add media metadata to result
            result["media_type"] = content_type
            result["media_filename"] = filename
            result["extracted_text"] = extracted_text

            print(f"\n✅ Multimodal fact-check complete!")
            print(f"Status: {result.get('status')}")
            print(f"{'='*60}\n")

            return result

        except Exception as e:
            error_msg = f"Error processing {content_type}: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "claim_text": claim_text or f"Media file: {filename}",
                "status": "❌ Error",
                "explanation": error_msg,
                "sources": [],
                "media_type": content_type,
                "error": str(e)
            }
