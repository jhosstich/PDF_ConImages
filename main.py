import os
import pathlib
from PyPDF2 import PdfReader
from GetImages import get_object_images

def main(path = None):
    if path is None:
        path = os.getcwd()
    desktop = pathlib.Path(path)
    #desktop.rglob("*")
    lista = os.listdir(path)
    conta = len(lista)
    archivos = []

    extract_dir = "extracts/"
    images_dir = "imagenTratada/"

    try:
        os.stat(extract_dir)
    except:
        os.mkdir(extract_dir)

    try:
        os.stat(images_dir)
    except:
        os.mkdir(images_dir)

    ##Ingresa a una lista los ficheros solo con extencion PDF, DOCX o DOC
    for i in range(conta):
        root, extension = os.path.splitext(lista[i])
        if extension == ".pdf" or extension == ".docx" or extension == ".doc":
            archivos.append(lista[i])

    conta2 = len(archivos)
    print(conta2)

    ## Recorremos la lista con los tipos de archivos validos 
    ## y leemos con PdfReader 

    for j in range(conta2):
        print(archivos[j])
        reader = PdfReader(archivos[j])

        print(j)
        print(archivos[j])
        print(len(reader.pages))
        pagesTotal =  len(reader.pages)
        print(pagesTotal)

        file, exten = os.path.split(archivos[j])
        filename = exten + ".txt"

        f = ""
        f = open("extracts/" + filename, 'w')
        page = ""
        text = ""
        image_number = 1 
        pagina = 1
        cont_images = 0
        pdf_filtered_images = [] 

        for numPage in range(pagesTotal):
            try:
                page = ""
                page = reader.pages[numPage]
                #extracting text from page
                text = page.extract_text()

                print("---------------------------------------------------")
                print("Page Number: " + str(numPage))
                #print(text)
                print("---------------------------------------------------")

                f.write(text)

                 ## GET Images

                try:
                    # Extraer objetos de las paginas
                    xObject = page['/Resources']['/XObject'].get_object()
                
                except KeyError:
                    continue

                cont_images, image_number, pdf_filtered_images = get_object_images(xObject, "imagenTratada/", image_number,archivos[j], exten, i + pagina, cont_images, pdf_filtered_images)  # Pasamos el número de página


            except NotImplementedError:
                print("Oops!  That was no valid number.  Try again...")
        f.close()

if __name__ == "__main__":
    main()