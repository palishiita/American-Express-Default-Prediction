# Databricks notebook code to convert CSV files in a zip to Parquet using Spark
from pyspark.sql import SparkSession
import zipfile
import io
from azure.storage.blob import BlobServiceClient

# Set up Azure BlobServiceClient
STORAGE_ACCOUNT_NAME = "amldatalakestore"
CONTAINER_NAME = "default-prediction-data"
ZIP_BLOB_NAME = "amex-default-prediction.zip"
AZURE_CONNECTION_STRING = "<your-azure-connection-string>"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

# Initialize Spark Session
spark = SparkSession.builder.appName("ConvertCSVtoParquet").getOrCreate()

# Function to download the ZIP file into memory
def download_zip_in_memory():
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blob_client = container_client.get_blob_client(ZIP_BLOB_NAME)
    print(f"Downloading {ZIP_BLOB_NAME} to memory...")
    stream = io.BytesIO()
    blob_client.download_blob().download_to_stream(stream)
    return stream

# Function to extract CSV files from the zip in memory and convert them to Parquet using Spark
def extract_and_convert_zip_to_parquet(zip_stream):
    with zipfile.ZipFile(zip_stream, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith('.csv'):
                print(f"Processing {file_name} from zip file...")
                with zip_ref.open(file_name) as csvfile:
                    # Read CSV directly into Spark DataFrame
                    df = spark.read.csv(io.TextIOWrapper(csvfile), header=True, inferSchema=True)
                    
                    # Convert CSV filename to Parquet filename
                    parquet_file_name = file_name.replace('.csv', '.parquet')
                    output_path = f"/mnt/default-prediction-data/{parquet_file_name}"
                    
                    # Write to Parquet in memory or directly to Azure Blob Storage
                    df.write.mode("overwrite").parquet(output_path)
                    print(f"Converted and saved {file_name} to Parquet at {output_path}.")

# Execute the workflow
if __name__ == "__main__":
    zip_stream = download_zip_in_memory()
    extract_and_convert_zip_to_parquet(zip_stream)