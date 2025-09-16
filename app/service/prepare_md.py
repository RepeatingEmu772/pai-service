from app.config.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def prepare_markdown():
    logging.info("Preparing markdown...")
    logging.info(settings.pg_connect_str)
