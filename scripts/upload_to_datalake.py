import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Storage Account and Container info
STORAGE_ACCOUNT_NAME = "amldatalakestore"
CONTAINER_NAME = "default-prediction-data"
FILE_PATH = "C:/Users/ishii/Desktop/American-Express-Default-Prediction/data/raw/amex-default-prediction.zip"
BLOB_NAME = "amex-default-prediction.zip"

# Authenticate using Azure Identity
credential = DefaultAzureCredential()

try:
    # Connect to the Data Lake Storage Account
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential
    )

    # Get the container client
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Upload the file with parallel uploads enabled
    logger.info("Starting file upload...")
    with open(FILE_PATH, "rb") as data:
        container_client.upload_blob(
            name=BLOB_NAME,
            data=data,
            overwrite=True,
            max_concurrency=4
        )

    logger.info(f"File '{FILE_PATH}' successfully uploaded to container '{CONTAINER_NAME}' as '{BLOB_NAME}'")

except HttpResponseError as e:
    logger.error(f"An HTTP error occurred: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")