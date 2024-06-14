from extract import analyser_texte_juridique
from preprocess import extract_text
from pathlib import Path
text = extract_text(Path('documents/pdf/AXELTIM - Actes du 01-04-2016.pdf'))
print('TEXT TO ANALYSE')
print(text)
print(analyser_texte_juridique(text))