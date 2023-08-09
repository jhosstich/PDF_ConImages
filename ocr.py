import os
import pytesseract
from PIL import Image

def tesseractOCR(image_path):

    # Verificar y crear el directorio si no existe
    if not os.path.exists("tesseract"):
        os.makedirs("tesseract")

    # Abrir la imagen con PIL
    img = Image.open(image_path)
    
    tessdata_dir_config = '--tessdata-dir "/home/jhoselin/tesseract/"'

    # Utilizar Tesseract para extraer texto
    text = pytesseract.image_to_string(img, lang='spa', config=tessdata_dir_config)
    # 'spa' es el código de idioma para español
    
    # Recuperar el nombre del archivo
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Creación y escritura de texto en el archivo ".txt"
    with open("tesseract" + "/" + "passport" + "_image_2" + file_name + ".txt", "w", encoding='utf-8') as f:
        print(text, file=f)

if __name__ == "__main__":
    folder_path = "./imagenTratada"
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        tesseractOCR(full_path)
