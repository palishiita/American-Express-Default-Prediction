import zipfile
import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import HttpResponseError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Storage Account and Container details
STORAGE_ACCOUNT_NAME = "amldatalakestore"
CONTAINER_NAME = "default-prediction-data"
ZIP_FILE_NAME = "amex-default-prediction.zip"
EXTRACTION_FOLDER = "unzipped_files"

# Authenticate using Azure Identity
credential = DefaultAzureCredential()

try:
    # Connect to Azure Data Lake Storage Account
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Download the zip file from the container
    logger.info(f"Downloading '{ZIP_FILE_NAME}' from container '{CONTAINER_NAME}'...")
    with open(ZIP_FILE_NAME, "wb") as zip_file:
        download_stream = container_client.download_blob(ZIP_FILE_NAME)
        zip_file.write(download_stream.readall())

    logger.info(f"'{ZIP_FILE_NAME}' downloaded successfully.")

except HttpResponseError as e:
    logger.error(f"An HTTP error occurred while downloading the zip file: {e}")
except Exception as e:
    logger.error(f"An unexpected error occurred: {e}")

# Unzipping the downloaded file
try:
    logger.info("Unzipping the file...")
    with zipfile.ZipFile(ZIP_FILE_NAME, 'r') as zip_ref:
        zip_ref.extractall(EXTRACTION_FOLDER)
    logger.info(f"'{ZIP_FILE_NAME}' unzipped successfully into '{EXTRACTION_FOLDER}'.")
except Exception as e:
    logger.error(f"An error occurred while unzipping the file: {e}")

# Convert CSV files to Parquet format
for csv_file in os.listdir(EXTRACTION_FOLDER):
    if csv_file.endswith('.csv'):
        csv_path = os.path.join(EXTRACTION_FOLDER, csv_file)
        try:
            logger.info(f"Converting '{csv_file}' to Parquet format...")
            df = pd.read_csv(csv_path)
            
            # Convert to Parquet using PyArrow
            table = pa.Table.from_pandas(df)
            parquet_file_path = csv_path.replace('.csv', '.parquet')
            pq.write_table(table, parquet_file_path)

            logger.info(f"'{csv_file}' converted to Parquet successfully.")

        except Exception as e:
            logger.error(f"An error occurred while converting '{csv_file}' to Parquet: {e}")

# Upload the Parquet files back to the container
for parquet_file in os.listdir(EXTRACTION_FOLDER):
    if parquet_file.endswith('.parquet'):
        parquet_file_path = os.path.join(EXTRACTION_FOLDER, parquet_file)
        try:
            logger.info(f"Uploading '{parquet_file}' to container '{CONTAINER_NAME}'...")
            with open(parquet_file_path, "rb") as data:
                container_client.upload_blob(
                    name=f"processed/{parquet_file}",
                    data=data,
                    overwrite=True
                )
            logger.info(f"'{parquet_file}' uploaded successfully.")
        
        except HttpResponseError as e:
            logger.error(f"An HTTP error occurred while uploading '{parquet_file}': {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while uploading '{parquet_file}': {e}")