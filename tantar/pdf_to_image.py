from tantar.utils.logger import get_logger
from tantar.settings import SETTINGS
import json

lambda_ = SETTINGS.lambda_.client
logger = get_logger(__name__)


def pdf2images(key, company_id):
    logger.info("call lambda to create images from pdf")
    response = lambda_.invoke(
        FunctionName="pdf_to_image",
        Payload=bytes(json.dumps({"key": key, "company_id": company_id}), "utf-8"),
    )
    try:
        images = json.loads(response["Payload"].read())
        body = json.loads(images["body"])
    except Exception as e:
        logger.error(f"Error decoding lambda response: {images}")
        return []
    return body
