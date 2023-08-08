# cd cgcpPdfToPngPrueba
# gcloud functions deploy convPdfToPng --timeout=540 --runtime python37 --trigger-resource 278460475211-b01 --project calidad-datos --trigger-event google.storage.object.finalize --region=europe-west3 --memory=1024 --clear-labels --update-labels agrupacion=dni-ucm --source "E:\DNI - JULIA\Fuentes\calidad-datos\convPdfToPng"

# Ultima version: 12/08/2020
# Ultima version: 19/09/2020 Se arreglan ciertas condiciones para el mover el PDF.
# Ultima version: 30/09/2020 Se arreglan ciertas condiciones para el mover el PDF.

#mimetype

#import keras_ocr

#docx documentos
import zipfile

#import easyocr

#import requests
from PIL import Image

#import cv2

import PyPDF2
import base64
import logging
import json
from PyPDF2 import generic
import tempfile
import os
import re
import time
from save_image import *
from datetime import datetime


config_file = 'config.json'

try:
    with open(config_file, 'r') as f:
        config = json.load(f)

    color_modes = config.get('color_modes')
    bucket_name = config.get('bucketName')
    filters = config.get('filters')
    function_name = config.get('function_name')
    resultados_ocr = config.get('resultadosocr')
except Exception as e:
    #logging.info(e)
    raise e



# función para extraer el espacio de color, en caso de error, se guarda en la carpeta errores
def get_color_mode(blob, obj, nombreFicheroResultado):
    # obtener el espacio de color del objeto
    try:
        mode = ''
        color_space = obj['/ColorSpace']
        #if '/ColorSpace' in obj:
            #logging.info(f'el espacio de color es {color_space}')
    except KeyError:
        return None
    try:
        if isinstance(color_space, generic.ArrayObject) and color_space[0] == '/Indexed':
            color_space, base, hival, lookup = [v.get_object() for v in color_space]
            mode = color_modes.get(base)
            dict_mode = {'mode': mode, 'color_space': color_space, 'base': base, 'hival': hival, 'lookup': lookup}
        elif isinstance(color_space, generic.ArrayObject) and color_space[0] == '/ICCBased':
            color_space, components = [v.get_object() for v in color_space]
            color = {1: '/Indexed', 3: '/DefaultRGB', 4: '/DefaultCMYK'}.get(components['/N'])
            mode = color_modes[color]
            dict_mode = {'mode': mode, 'color_space': color_space, 'components': components}
        elif isinstance(color_space, generic.ArrayObject) and color_space[0] == '/Separation':
            color_space, name, alternateSpace, tintTransform = [v.get_object() for v in color_space]
            mode = color_modes.get(name, alternateSpace)
            dict_mode = {'mode': mode, 'color_space': color_space, 'name': name, 'alternateSpace': alternateSpace,
                         'tintTransform': tintTransform}
        else:
            mode = color_modes[color_space]
            dict_mode = {'mode': mode}
        return dict_mode
    except Exception as e:
        if mode == '':
            print('Error grabando imagen, no existe el parámetro color . Exception:' + str(e))
        else:
            print('Error grabando imagen con color ' + mode + '. Exception:' + str(e))
        pass
        # raise e


def get_object_images(xObject, file_dest, image_number, blob, file_name, pagina, cont_images, pdf_filtered_images):
    # Obtener los objetos (imágenes) de cada página del pdf
    try:
        """Triggered by a change to a Cloud Storage bucket.
            Args:
                    event (dict): Event payload.
                    context (google.cloud.functions.Context): Metadata for the event.
            """
        # all_images_ok = True
        images = []  # lista de imágenes
        # image_number = 0 #inicializo a 0 el número de imagenes de la página actual
        decode_parms = None
        decode_images = True
        nombreFicheroResultado = ''
        # mask = None
        # función que simula un switch, en caso de que el dato venga comprimido, se descomprime
        def switch_decode(sub_obj, dict_mode, filter, data, image_name, decode_parms=None):
            try:
                switcher = {
                    # si la imagen es .png
                    # descomprimimos el objeto
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/FlateDecode' or '/Fl': lambda: flateDecode(data, decode_parms),
                    # si la imagen es .tiff
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/CCITTFaxDecode' or '/CCF': lambda: tiff_decode(data, sub_obj),
                    # si la imagen es .tif
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/LZWDecode' or '/LZW': lambda: lzwDecode(data, decode_parms),
                    # si la imagen es .jpeg/jpg
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/DCTDecode' or '/DCT': lambda: dctDecode(data, decode_parms, dict_mode),
                    # si la imagen es .jp2
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/JPXDecode': lambda: data,
                    # si la imagen está comprimida con ASCII85encode
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/ASCII85Decode' or '/A85': lambda: base64.a85decode(sub_obj._data, adobe=True),
                    # si la imagen está comprimida con ASCIIHexDecode
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/ASCIIHexDecode' or '/AHx': lambda: asciiHexDecode(data),
                    # si la imagen está comprimida con runLengthDecode
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/runLengthDecode' or '/RL': lambda: runLengthDecode(data),
                    # si la imagen está comprimida con JBIG2Decode
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/JBIG2Decode': lambda: data,
                    # si la imagen viene en crudo ( sin filtro)
                    'raw': lambda: data
                }
                return switcher.get(filter)()
            except Exception as e:
                raise e

        # función que simula un switch,dependiendo del tipo de compresión se guarda de una forma o de otra
        def switchcase(page, dict_mode, size, filter, data, image_name, decode_params=None, mask=0):
            try:
                switcher = {
                    # si la imagen es .png
                    # descomprimimos el objeto
                    # guardamos en la lista el color, ancho, alto y la imagen
                   
                   
                    '/FlateDecode': lambda: save_flate_image( file_dest,page, dict_mode,
                                                             size,
                                                             data, image_name, filter, decode_params),
                    # si la imagen es .tiff
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/CCITTFaxDecode': lambda: save_tiff_image( file_dest, page, data, sub_obj,
                                                               image_name, filter, dict_mode['mode'],
                                                               size, decode_params),
                    # si la imagen es .tif
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/LZWDecode': lambda: save_lzw_image( file_dest, page, dict_mode['mode'],
                                                         size, data,
                                                         image_name, filter),
                    # si la imagen es .jpeg/jpg
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/DCTDecode': lambda: save_dct_image( file_dest, page, data,
                                                         dict_mode['mode'],
                                                         size,
                                                         image_name, filter, decode_params),

                    '/ASCII85Decode': lambda: save_png_page( file_dest, page, dict_mode['mode'],
                                                            size,
                                                            base64.a85decode(sub_obj._data, adobe=True), image_name,
                                                            filter),
                    # si la imagen es .jp2
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/JPXDecode': lambda: save_jpx_image( file_dest, page, data,
                                                         dict_mode['mode'],
                                                         size,
                                                         image_name, filter),
                    # si la imagen es .jp2
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/JBIG2Decode': lambda: save_jbig2_image( file_dest, page, data,
                                                             dict_mode['mode'],
                                                             size,
                                                             image_name, filter),
                    # si la imagen es .jp2
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/ASCIIHexDecode': lambda: save_ASCIIHex_image( file_dest, page, data,
                                                                   dict_mode['mode'],
                                                                   size,
                                                                   image_name, filter),
                    # si la imagen es .jp2
                    # guardamos en la lista el color, ancho, alto y la imagen
                    '/runLengthDecode': lambda: save_runLength_image( file_dest, page,
                                                                     dict_mode['mode'],
                                                                     size, data,
                                                                     image_name, filter),
                    # si la imagen viene en crudo ( sin filtro)
                    'raw': lambda: save_raw_image( file_dest, page, dict_mode['mode'],
                                                  size, data,
                                                  image_name, filter)
                }
                return switcher.get(filter)()
            except Exception as e:
                raise e

        for obj_name in xObject:  # recorremos cada uno de los objetos
            try:
                
                sub_obj = xObject[obj_name]
                if '/Resources' in sub_obj and '/XObject' in sub_obj['/Resources']:
                    cont_images, image_number, pdf_filtered_images = get_object_images( sub_obj['/Resources']['/XObject'].get_object(), blob, file_name, pagina, cont_images, image_number,
                    pdf_filtered_images)
                    # Para los objetos que sean tipo imagen
                elif sub_obj['/Subtype'] == '/Image':  # si el subtipo del objeto es una imagen
                    try:
                        # Incrementar numero de imagen
                        # image_number = image_number + 1
                        # Nombre del fichero nuevo
                        # nombreFicheroResultado = f"{file_name}-{image_number}" #Guardamos el número de página también en el nombre del fichero
                        nombreFicheroResultado = f"{file_name}-{image_number}"  # Guardamos el número de página también en el nombre del fichero
                        data = sub_obj._data
                        filt = xObject[obj_name].get('/Filter', 'raw')
                        size = (sub_obj['/Width'], sub_obj['/Height'])
                        '''if '/Mask' in sub_obj:#TODO aceptar el parámetro MASK ( sobre todo para filtros ccitfaxdecode)
                            sub_obj = sub_obj['/Mask']'''
                        if '/DecodeParms' in sub_obj:
                            decode_parms = sub_obj['/DecodeParms']
                        dict_mode = get_color_mode(blob, sub_obj, nombreFicheroResultado)
                        #logging.info(f'variable dict_color {dict_mode} y su data {sub_obj}')
                        if dict_mode is not None:  # comprobamos que la imagen tiene el diccionario 'color_sapace'
                            if isinstance(filt, list):
                                decode_images = True
                                while len(
                                        filt) > 1:  # en caso de que vengan mas de un filtro, se recorre la lista aplicando cada filtro
                                    # y su resultado se pasa al siguiente filtro de forma recursiva hasta llegar al ultimo
                                    first_filter = filt.pop(0)
                                    # #logging.info(first_filter)
                                    data = switch_decode(sub_obj, dict_mode, first_filter, data,
                                                         nombreFicheroResultado,
                                                         decode_parms)  # devuelve una tupla(estado y el stream decodificado)
                                    if data[0] != 0:  # si se ha producido algún error en la decompresión de la imagen salimos del bucle
                                        decode_images = False
                                        break
                                    else:  # en caso de éxito (data[0] = 1, guardamos la decompresión del primer filtro
                                        # como entrada para el segundo filtro
                                        data = data[1]
                                filt = filt[0]  # se obtiene el ultimo filtro
                            if (decode_images):  # si se han descomprmido todas las compresiones de la lista,
                                # finalemente guardamos la imagen
                                if filt in filters:  # comprobamos que el filtro está en la lista de filtros conocidos
                                    #logging.info(f'el valor del filtro {filt}')
                                    result = switchcase(pagina, dict_mode, size, filt, data,
                                                        nombreFicheroResultado, decode_parms)
                                    #logging.info(f'el valor de result {result}')
                                    if result[0]:
                                        cont_images = cont_images + 1  # contador de imagenes guardadas
                                        if len(result) > 0:
                                            pdf_filtered_images.append(result[1])
                                else:
                                    print("Error switchcase")
                                image_number += 1
                            else:
                                filt = xObject[obj_name].get('/Filter', 'raw')
                                print(text = 'Error al decodificar la imagen con filtro: ' + filt)
                        else:  # en caso de que la imagen no tenga el diccionario 'color_space' se genera un error
                            print('Error grabando imagen, sin espacio de color con filtro' + filt)
                    except Exception as e:  # en caso de que algo haya salido mal, guardamos el error en la carpeta errores
                        filt = xObject[obj_name].get('/Filter', 'raw')
                        print('Error grabando imagen con filtro' + filt + '. Exception:' + str(e))
            except Exception as e:
                print(text = ' Exception:' + str(e))
        return images
    except Exception as e:
        print(text = ' Exception:' + str(e))
    finally:
        return cont_images, image_number, pdf_filtered_images

docsPath = ""