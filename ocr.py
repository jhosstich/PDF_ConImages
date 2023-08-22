import os
import numpy as np
import pytesseract
from PIL import Image
import cv2
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Usa la ruta que te dio el comando 'which'
pytesseract.pytesseract.temp_dir = '/home/jhoselin/tesseract'

def tesseractOCR(image_path):

    # Verificar y crear el directorio si no existe
    if not os.path.exists("tesseract"):
        os.makedirs("tesseract")
    
    # Define the folder and ensure it exists
    output_folder = "./modified_images"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not os.path.exists(pytesseract.pytesseract.temp_dir):
        os.makedirs(pytesseract.pytesseract.temp_dir)
        
    # Abrir la imagen con PIL
    img = Image.open(image_path)

    tessdata_dir_config = '--tessdata-dir "/home/jhoselin/tesseract/"'

    # Convertir la imagen PIL a formato OpenCV
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Detectar la posición del texto original
    data = pytesseract.image_to_data(img, lang='spa', output_type=pytesseract.Output.DICT)
    print(data)

    num_words = len(data['text'])
    for i in range(num_words):
        word = data['text'][i]
        x = data['left'][i]
        y = data['top'][i]
        w = data['width'][i]
        h = data['height'][i]
        
        # Ahora puedes procesar cada palabra y sus coordenadas como desees
        if word == "Loterías":
            # "Borrar" el texto original
            cv2.rectangle(img_cv, (x, y), (x+w, y+h), (255, 255, 255), -1)
            
            # Definir la fuente y tamaño del texto para OpenCV
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            font_color = (138,221,45)  # Color
            thickness = 2
            
            # Escribir el texto modificado en la misma posición
            cv2.putText(img_cv, "xxxxxx", (x, y+h), font, font_scale, font_color, thickness, cv2.LINE_AA)
            

    # Specify the filename (you can modify this as needed)
    filename = os.path.basename(image_path)

    # Guardar la imagen modificada in the new folder
    cv2.imwrite(os.path.join(output_folder, filename), img_cv)

    # Recuperar el nombre del archivo
    file_name = os.path.splitext(os.path.basename(image_path))[0]
    # Utilizar Tesseract para extraer texto
    text = pytesseract.image_to_string(img, lang='spa', config=tessdata_dir_config)
    # 'spa' es el código de idioma para español
    # Creación y escritura de texto en el archivo ".txt"
    with open("tesseract" + "/" + "passport" + "_image_2" + file_name + ".txt", "w", encoding='utf-8') as f:
        print(text.replace("Loterías", "xxxxxx"), file=f)

if __name__ == "__main__":
    folder_path = "./imagenTratada"
    for file in os.listdir(folder_path):
        full_path = os.path.join(folder_path, file)
        tesseractOCR(full_path)
