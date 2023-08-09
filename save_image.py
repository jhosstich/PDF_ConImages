from decompress import *
from io import BytesIO
from PIL import Image, ImageEnhance
import os, tempfile
import logging
import json
#from main_filters import *
#############funciones para guardar una imagen según la compresión utilizada############################
# guardar la imagen en caso de que venga en crudo (sin filtro)

config_file = 'config.json'

try:
    with open(config_file, 'r') as f:
        config = json.load(f)
    function_name = config.get('function_name')
    resultados_ocr = config.get('resultadosocr')
except Exception as e:
    logging.info(e)
    raise e

def set_image_dpi(image):
    '''
       Scaling of image, Image Rescaling is important for image analysis.
       Mostly OCR engine give an accurate output of the image which has 300 DPI.
        DPI describes the resolution of the image or in other words, it denotes logging.infoed dots per inch.'
        @param image: image to scale
        @return: Image resize
    '''

    length_x, width_y = image.size
    factor = min(1, float(1024.0 / length_x))
    size = int(factor * length_x), int(factor * width_y)
    im_resized = image.resize(size, Image.LANCZOS)
    return im_resized

def run_filters(fileName, page):
    try:
        # filtrar la imagen y guardarla en un diccionario (clave: nombre imagen, valor: imagen filtrada
        #image_filtered_name = fgcpFiltrosPrueba(fileName, page)
        #image_filtered_name += '_filtered'
        #return image_filtered_name
        return fileName
    except Exception as e:
        logging.info('error en run_filters')
        raise e
    
    
    
######################las imagenes y las imagenes filtradas  se guardan en la carpeta tratarFiltrados#############

def save_raw_image( file_dest, page, mode, size, data, fileName, filter):
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        img = Image.frombytes(mode, size, data)
        img.save(nombre, format='PNG')
        # Subir contenido del fichero temporal
        saved_image = True
        if saved_image:
            nombre = run_filters(fileName, page)

    except Exception as e:
        print('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result
    

def save_tiff_image( file_dest, page, data, sub_obj, fileName, filter, mode, size, decode_params=None):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        try:
            data = tiff_decode(data, sub_obj)
            if data[0] == 0:
                img = Image.frombytes(mode, size, data[1])
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(
                    im_resized)  # mejoramos la nitidez de la imagen  #mejoramos la nitidez de la imagen
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(file_dest, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            else:
                print('Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro tiff.' \
                                                                    'Error en la decodificación ')

        except Exception as e:
            try:
                img = Image.open(BytesIO(data[1]))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre,'.png'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
                    # Subir contenido del fichero temporal
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)

                except Exception as e:
                    print('Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro tiff. ' \
                                                                         'Error en la decodificación ')
                    pass
                # img.close()
                pass
            pass
        except Exception as e:
            text = ('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
            print(text)
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_ASCIIHex_image(file_dest, page, data, mode, size, fileName, filter):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        try:
            data = asciiHexDecode(data)
            if data[0] == 0:  # si no hay errores, entonces guardamos
                img = Image.frombytes(mode, size, data[1])
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            else:
                print('error al decodificar la iamgen con filtro flateDecode')
        except Exception  as e:
            try:
                img = Image.open(BytesIO(data[1]))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception  as e:
                try:
                    img = open(os.path.join(nombre + '.png'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
                    # Subir contenido del fichero temporal
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)

                except Exception  as e:
                    print('Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro ASCIIHex. '
                                                                          'Error en la decodificación ')
                    pass
                pass
            pass
    except Exception as e:
        print('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_runLength_image(file_dest, page, mode, size, data, fileName, filter, decode_params=None):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        try:
            data = runLengthDecode(data)
            if data[0] == 0:  # si no hay errores, entonces guardamos
                img = Image.frombytes(mode, size, data[1])
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            else:
                print('error al decodificar la iamgen con filtro flateDecode')
        except Exception as e:
            try:
                img = Image.open(BytesIO(data[1]))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre + '.png'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
                    # Subir contenido del fichero temporal
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)

                except Exception as e:

                    text = ('Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro runLength. '
                                                                          'Error en la decodificación ')
    
                    pass
                # img.close()
                pass
            pass
    except Exception as e:
        print('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_lzw_image(file_dest, page, mode, size, data, fileName, filter, decode_params=None):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        # Obtener el nuevo fichero del bucket
        try:
            data = lzwDecode(data, decode_params)
            if data[0] == 0:  # si no hay errores,  entonces guardamos
                img = Image.frombytes(mode, size, data[1])
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            else:
                text = ('error al decodificar la iamgen con filtro lzwDecode')

        except Exception as e:
            try:
                img = Image.open(BytesIO(data[1]))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre, '.png'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
                    # Subir contenido del fichero temporal
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)

                except Exception as e:

                    text = ('Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro lzw. '
                                                                          'Error en la decodificación ')
                    pass
                pass
            pass
    except Exception as e:

        text = ('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
        print(text)
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_png_page( file_dest, page, mode, size, data, fileName, filter, decode_params=None):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        # Obtener el nuevo fichero del bucket
        try:
            img = Image.frombytes(mode, size, data)
            im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
            enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
            img_enchacer = enhancer.enhance(2.0)
            img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
            saved_image = True
            if saved_image:
                nombre = run_filters(fileName, page)

        except Exception as e:
            try:
                img = Image.open(BytesIO(data))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre,'.png'), "wb")
                    img.write(bytearray(data))
                    img.close()
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)

                except Exception as e:
                    text = ('Error grabando imagen con filtro: ' + filter)
    
                # img.close()
                pass
            pass
    except Exception as e:
        text = 'Error grabando imagen con filtro' + filter + '. Exception:' + str(e)
        print(text)
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_dct_image( file_dest, page, data, mode, size, fileName, filter, decode_params=None):
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        try:
            data = dctDecode(data, decode_params, mode)
            if data[0] == 0:
                img = Image.open(BytesIO(data[1]))  # Image.frombytes(mode, size, data)
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen#
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(nombre, page)

            else:

                text = 'Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro dctdecode. ' \
                                                                    'Error en la decodificación '
                print(text)

        except Exception as e:
            try:
                img = Image.frombytes(mode, size, data[1])  # Image.open(BytesIO(data))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen#
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                #logging.info('subida al bucket frombytes')
                #logging.info(f'se ha tenido que guardar la imagen')
                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre,'.jpg'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
    
                    #logging.info('subida al bucket ')
                    #logging.info(f'ultimo intento de guardado')
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)


                except Exception as e:

                    text = 'Error grabando imagen con filtro' + filter + '. Error grabando PNG con filtro dct.' \
                                                                        'Error en la decodificación '
                    print(text)
                    pass
                pass
            pass
    except Exception as e:
        text = 'Error grabando imagen con filtro' + filter + '. Exception:' + str(e)
        print(text)
    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result

def save_jbig2_image( file_dest, page, data, mode, size, fileName, filter, decode_params=None, mask=None):
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"

        try:
            img = Image.frombytes(mode, size, data)
            im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
            enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
            img_enchacer = enhancer.enhance(2.0)
            img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
            # Subir contenido del fichero temporal
            saved_image = True
        except Exception as e:
            try:
                img = Image.open(BytesIO(data))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join( nombre,'.png'), "wb")
                    img.write(bytearray(data))
                    img.close()
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)


                except Exception as e:
                    print('Error grabando imagen con filtro: ' + filter)
                    pass
                # img.close()
                pass
            pass
    except Exception as e:
        print('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))
    finally:
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result
    
def save_jpx_image(file_dest, page, data, mode, size, fileName, filter, decode_params=None, mask=None):
    try:
        result = []
        saved_image = False

        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"

        try:
            img = Image.frombytes(mode, size, data)
            im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
            enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
            img_enchacer = enhancer.enhance(2.0)
            img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
            # Subir contenido del fichero temporal
            saved_image = True
        except Exception as e:
            try:
                img = Image.open(BytesIO(data))
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal

                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(nombre, '.png'), "wb")
                    img.write(bytearray(data))
                    img.close()
                    # Subir contenido del fichero temporal
    
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)


                except Exception as e:
                    print('Error grabando imagen con filtro: ' + filter)    
                    pass
                # img.close()
                pass
            pass
    except Exception as e:
        print(('Error grabando imagen con filtro' + filter + '. Exception:' + str(e)))
    finally:
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(nombre)
        return result    
    

def save_flate_image(file_dest, page, dict_mode,
                     size, data, fileName, filter, decode_params=None):
    # Almacenar PNG
    try:
        result = []
        saved_image = False

        #_, nombre = tempfile.mkstemp()
        # Almacenar nuevo nombre
        nombre = file_dest + fileName + ".png"
        try:
            data = flateDecode(data, decode_params)
            mode = 'RGB'
            if data[0] == 0:  # si no hay errores, entonces guardamos
                if 'mode' in dict_mode:
                    mode = dict_mode.get('mode')
                img = Image.frombytes(mode, size, data[1])
                # en caso de que el espacio de color sea 'indexed', entonces tenemos que revisar la matriz y recuperar
                # la paleta indexada
                if ('color_space' in dict_mode) and (dict_mode.get('color_space') == '/Indexed'):
                    if 'lookup' in dict_mode and mode == 'RGB':
                        lookup = dict_mode.get('lookup')
                        img.putpalette(lookup, mode)
                        img = img.convert(mode)
                    else:  # Pillow's ImagePalette only supports RGB
                        if mode in {'RGBA', 'CMYK'}:
                            n = 4
                        else:
                            n = 3
                        palette = dict_mode.get('lookup')
                        palette = [palette[i:i + n] for i in range(0, len(palette), n)]
                        data2 = b''.join([palette[b] for b in data])
                        img = Image.frombytes(mode, size, data2)

                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                                                                                                     
                img_enchacer.save(nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal
                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            else:
                print('error al decodificar la imagen con filtro flateDecode')                
        except Exception as e:
            try:
                mode = 'RGB'
                img = Image.open(BytesIO(data[1]))
                if ('color_space' in dict_mode) and (dict_mode.get('color_space') == '/Indexed'):
                    if 'lookup' in dict_mode and mode == 'RGB':
                        lookup = dict_mode.get('lookup')
                        img.putpalette(lookup, mode)
                        img = img.convert(mode)
                    else:  # Pillow's ImagePalette only supports RGB
                        if mode in {'RGBA', 'CMYK'}:
                            n = 4
                        else:
                            n = 3
                        palette = dict_mode.get('lookup')
                        palette = [palette[i:i + n] for i in range(0, len(palette), n)]
                        data2 = b''.join([palette[b] for b in data])
                        img = Image.frombytes(mode, size, data2)
                im_resized = set_image_dpi(img)  # mejoramos la resolución de la imagen (DPI)
                enhancer = ImageEnhance.Sharpness(im_resized)  # mejoramos la nitidez de la imagen  #
                img_enchacer = enhancer.enhance(2.0)
                img_enchacer.save(file_dest + nombre, optimize=True, dpi=(300, 300), quality=95, format='PNG')
                # Subir contenido del fichero temporal
                saved_image = True
                if saved_image:
                    nombre = run_filters(fileName, page)


            except Exception as e:
                try:
                    img = open(os.path.join(file_dest + nombre, '.png'), "wb")
                    img.write(bytearray(data[1]))
                    img.close()
                    saved_image = True
                    if saved_image:
                        nombre = run_filters(fileName, page)


                except Exception as e:
                    print('Error grabando imagen con filtro: ' + filter)
                    pass
                pass
            pass
    except Exception as e:
        print('Error grabando imagen con filtro' + filter + '. Exception:' + str(e))

    finally:
        result.append(saved_image)
        if saved_image:  # si se ha guardado la imagen entonces insertamos la imagen filtrada en la lista
            result.append(file_dest + nombre + '.png')
        return result