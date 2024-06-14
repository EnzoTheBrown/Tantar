from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import base64
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = FastAPI()

# AWS S3 configuration - replace with your actual values

S3_BUCKET_NAME = 'tantar'

# Initialize the S3 client
s3_client = boto3.client('s3')

class FileUpload(BaseModel):
    file_name: str
    file_content: str

@app.post("/upload/")
async def upload_file(file: FileUpload):
    try:
        # Decode the base64 file content
        file_data = base64.b64decode(file.file_content)
        
        # Upload the file to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file.file_name,
            Body=file_data
        )
        
        # Construct the S3 file URL
        s3_url = f"https://{S3_BUCKET_NAME}.s3.eu-west-1.amazonaws.com/{file.file_name}"
        return {"s3_url": s3_url}
    
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=403, detail="Invalid AWS credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)