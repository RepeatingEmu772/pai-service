from fastapi import APIRouter
import logging
from ..service.prepare_md import prepare_markdown
from ..model.chat import chatRequest
from ..service.fetch import fetch_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter(
    prefix="/chat",
)

@router.get("/text")
async def get_chat_response():
    logging.info("Getting chat response...")
    prepare_markdown()
    return {"message": "This is a placeholder for ChatGPT response"}

@router.post("/text")
async def post_chat_response(request: chatRequest):
    logging.info("Posting chat response...")
    results = fetch_data(query=request.message)
    return {"message": f"Received message: {request.message}", "results": results}