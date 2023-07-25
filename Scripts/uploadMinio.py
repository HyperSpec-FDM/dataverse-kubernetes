from minio import Minio
from minio.error import S3Error

# Initialize MinIO client
minio_client = Minio(
    endpoint="127.0.0.1:9000",
    access_key="5IMXGis0YjH6620GIH16",
    secret_key="iJAI9HhY8RUW8RWjF0gt7lYZ9yxMKtFfuhlfrxLK",
    secure=False  # Change to True if using HTTPS
)

def upload_file(bucket_name, file_path, object_name):
    try:
        # Check if the bucket already exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Upload the file
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path
        )

        print("File uploaded successfully.")
    except S3Error as e:
        print(f"Error uploading file: {e}")

# Usage example
bucket_name = "hsma"
file_path = "deploy.py"
object_name = "deploy.py"

upload_file(bucket_name, file_path, object_name)
