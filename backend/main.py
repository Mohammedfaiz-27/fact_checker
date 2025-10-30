from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.claim_api import router as claim_router
from app.core.config import FRONTEND_URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # React dev frontend URL from .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claim_router, prefix="/api/claims")

@app.get("/")
async def root():
    return {"message": "Fact Checker API is running. Use /api/claims endpoint."}
