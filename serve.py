from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError
from PIL import Image
from io import BytesIO
import base64
import PyPDF2
from surya.ocr import run_ocr
from surya.model.detection import segformer
from surya.model.recognition.model import load_model
from surya.model.recognition.processor import load_processor

app = FastAPI()

# Initialize S3 client
s3 = boto3.client('s3')

class PDFBase64(BaseModel):
    file: str
    bucket: str
    filename: str

def save_pdf_to_s3(pdf_base64: str, bucket: str, filename: str):
    try:
        pdf_data = base64.b64decode(pdf_base64)
        s3.put_object(Bucket=bucket, Key=filename, Body=pdf_data)
        return f's3://{bucket}/{filename}'
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="S3 credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def convert_pdf_to_image(pdf_path: str):
    s3.download_file(pdf_path.split('/')[2], pdf_path.split('/')[-1], '/tmp/temp.pdf')
    with open('/tmp/temp.pdf', "rb") as f:
        reader = PyPDF2.PdfFileReader(f)
        page = reader.getPage(0)
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(page)
        pdf_output = BytesIO()
        pdf_writer.write(pdf_output)
        pdf_output.seek(0)
        image = Image.open(pdf_output)
        return image

def ocr(image: Image.Image):
    langs = ["fr"]
    det_processor, det_model = segformer.load_processor(), segformer.load_model()
    rec_model, rec_processor = load_model(), load_processor()
    predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
    return predictions

@app.post("/upload-pdf/")
async def upload_pdf(pdf: PDFBase64):
    try:
        # Save the PDF to S3
        pdf_path = save_pdf_to_s3(pdf.file, pdf.bucket, pdf.filename)
        
        # Convert the PDF to an image
        image = convert_pdf_to_image(pdf_path)
        
        # Perform OCR on the image
        preds = ocr(image)
        
        # Extract text from OCR results
        text = '\n'.join('\n'.join(p.text for p in pred.text_lines) for pred in preds)
        
        return JSONResponse(content={"text": text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
