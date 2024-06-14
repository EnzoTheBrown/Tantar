import pypdf
import pathlib
import os
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from ocr import ocr
from PIL import Image


PATH = pathlib.Path('documents')
PDF_PATH = PATH / 'pdf'
IMAGE_PATH = PATH / 'image'


def pdf2text(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf_reader = pypdf.PdfReader(f)
        text = '\n'.join(page.extract_text() for page in pdf_reader.pages)
        return text


def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Unable to load image {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(gray, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img

def extract_text_from_image(image_path):
    # processed_image = preprocess_image(str(image_path))
    text = ocr(Image.open(image_path)) #  pytesseract.image_to_string(processed_image, config='--psm 6', lang='fra')
    return text


def pdf2image(pdf_path, document_image_path):
    images = convert_from_path(pdf_path, dpi=200)
    for i, image in enumerate(images):
        image_path = document_image_path / f"{i}.png"
        image.save(image_path, 'PNG')


def extract_text(document_path):
    file_name = document_path.name
    print(f'########## {file_name} ##########')
    image_name = file_name.split('.')[0]
    document_image_path = IMAGE_PATH / image_name
    try:
        document_image_path.mkdir()
        pdf2image(document_path, document_image_path)
    except FileExistsError:
        pass

    image_names = os.listdir(document_image_path)
    
    return '\n######### NEW PAGE #########\n'.join(extract_text_from_image(document_image_path / image_name) for image_name in image_names)
