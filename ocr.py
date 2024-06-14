from PIL import Image
from surya.ocr import run_ocr
from surya.model.detection import segformer
from surya.model.recognition.model import load_model
from surya.model.recognition.processor import load_processor


def ocr(image: Image.Image):
    langs = ["fr"]
    det_processor, det_model = segformer.load_processor(), segformer.load_model()
    rec_model, rec_processor = load_model(), load_processor()

    predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)

    return ' '.join([pred.text_line for pred in predictions[0]])
