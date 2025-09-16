from fastapi import APIRouter
import logging
from ..service.prepare_md import prepare_markdown

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