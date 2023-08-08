from skimage.color import yuv2rgb
import lzw3
import re
import zlib
import struct
import logging

####################################funciones para decodificar la imagen####################################
def getBitsFromNum(num, bitsPerComponent=8):
    '''
        Makes the conversion between number and bits

        @param num: Number to be converted
        @param bitsPerComponent: Number of bits needed to represent a component
        @return: A tuple (status,statusContent), where statusContent is the string containing the resulting bits in case status = 0 or an error in case status = -1
    '''
    if not isinstance(num, int):
        return (-1, 'num must be an integer')
    if not isinstance(bitsPerComponent, int):
        return (-1, 'bitsPerComponent must be an integer')
    try:
        bitsRepresentation = bin(num)
        bitsRepresentation = bitsRepresentation.replace('0b', '')
        mod = len(bitsRepresentation) % 8
        if mod != 0:
            bitsRepresentation = '0' * (8 - mod) + bitsRepresentation
        bitsRepresentation = bitsRepresentation[-1 * bitsPerComponent:]
    except:
        return (-1, 'Error in conversion from number to bits')
    return (0, bitsRepresentation)

def getNumsFromBytes(bytes_, bitsPerComponent=8):
    '''
        Makes the conversion between bytes and numbers, depending on the number of bits used per component.

        @param bytes: String representing the bytes to be converted
        @param bitsPerComponent: Number of bits needed to represent a component
        @return: A tuple (status,statusContent), where statusContent is a list of numbers in case status = 0 or an error in case status = -1
    '''
    if not isinstance(bitsPerComponent, int):
        return (-1, 'bitsPerComponent must be an integer')
    outputComponents = []
    bitsStream = ''
    for byte in bytes_:
        try:
            bitsRepresentation = bin(ord(byte))
            bitsRepresentation = bitsRepresentation.replace('0b', '')
            bitsRepresentation = '0' * (8 - len(bitsRepresentation)) + bitsRepresentation
            bitsStream += bitsRepresentation
        except:
            return (-1, 'Error in conversion from bytes to bits')

    try:
        for i in range(0, len(bitsStream), bitsPerComponent):
            bytes = ''
            bits = bitsStream[i:i + bitsPerComponent]
            num = int(bits, 2)
            outputComponents.append(num)
    except:
        return (-1, 'Error in conversion from bits to bytes')
    return (0, outputComponents)

def getBytesFromBits(bitsStream):
    '''
        Makes the conversion between bits and bytes.

        @param bitsStream: String representing a chain of bits
        @return: A tuple (status,statusContent), where statusContent is the string containing the resulting bytes in case status = 0 or an error in case status = -1
    '''
    if not isinstance(bitsStream, str):
        return (-1, 'The bitsStream must be a string')
    bytes_ = b''
    if re.match('[01]*$', bitsStream):
        try:
            for i in range(0, len(bitsStream), 8):
                bits = bitsStream[i:i + 8]
                byte = chr(int(bits, 2)).encode()
                bytes_ += bytes(byte)
        except:
            return (-1, 'Error in conversion from bits to bytes')
        return (0, bytes)
    else:
        return (-1, 'The format of the bit stream is not correct')
    ##############Funciones para decodificar/descomprimir una imagen segun sea el filtro de compresión ##################

def asciiHexDecode(data):
    '''
        Method to decode streams using hexadecimal encoding

        @param stream: A PDF stream
        @return: A tuple (status,statusContent), where statusContent is the decoded PDF stream in case status = 0 or an error in case status = -1
    '''
    try:
        eod = '>'
        decodedStream = ''
        char = ''
        index = 0
        while index < len(data):
            c = data[index]
            if c == eod:
                if len(decodedStream) % 2 != 0:
                    char += '0'
                    try:
                        decodedStream += chr(int(char, base=16))
                    except:
                        return (-1, 'Error in hexadecimal conversion')
                break
            elif c.isspace():
                index += 1
                continue
            char += c
            if len(char) == 2:
                try:
                    decodedStream += chr(int(char, base=16))
                except:
                    return (-1, 'Error in hexadecimal conversion')
                char = ''
            index += 1
        return (0, decodedStream)
    except Exception as e:
       raise e

def flateDecode(data, parameters):
    '''
           Método para decodificar la imagen usando cuando esta ha sido codificada con el algoritmo Flate

           @param data: Imagen
           @return: Una tupla (status,statusContent), donde statusContent es la imagen decodificada en caso de que status= 0
            o un error en caso de que status = -1
       '''
    decoded_data = ''
    try:
        decoded_data = zlib.decompress(data)
    except:
        return (-1, 'Error decompressing string')

    if parameters == None or parameters == {}:
        return (0, decoded_data)
    else:
        if '/Predictor' in parameters:
            predictor = parameters['/Predictor']
        else:
            predictor = 1
        # Columns = number of samples per row
        if '/Columns' in parameters:
            columns = parameters['/Columns']
        else:
            columns = 1
        # Colors = number of components per sample
        if '/Colors' in parameters:
            colors = parameters['/Colors']
            if colors < 1:
                colors = 1
        else:
            colors = 1
        # BitsPerComponent: number of bits per color component
        if '/BitsPerComponent' in parameters:
            bits = parameters['/BitsPerComponent']
            if bits not in [1, 2, 4, 8, 16]:
                bits = 8
        else:
            bits = 8
        if predictor != None and predictor != 1:
            ret = post_prediction(decoded_data, predictor, columns, colors, bits)
            return ret
        else:
            return (0, decoded_data)

def lzwDecode(data, parameters):
    '''
             Método para decodificar la imagen usando cuando esta ha sido codificada con el algoritmo LZW

             @param data: Imagen
             @return: Una tuple (status,statusContent), donde statusContent es la imagen decodificada en caso de que status= 0
              o un error en caso de que status = -1
         '''
    decoded_data = ''
    try:
        decoded_data = lzw3.decompress(data)
    except Exception as e:
        logging.info(e)
        return (-1, 'Error decompressing string')

    if parameters == None or parameters == {}:
        for e in decoded_data:
            logging.info(e)
        return (0, decoded_data)
    else:
        if '/Predictor' in parameters:
            predictor = parameters['/Predictor']
        else:
            predictor = 1
            # Columns = number of samples per row
        if '/Columns' in parameters:
            columns = parameters['/Columns']
        else:
            columns = 1
            # Colors = number of components per sample
        if '/Colors' in parameters:
            colors = parameters['/Colors']
            if colors < 1:
                colors = 1
        else:
            colors = 1
            # BitsPerComponent: number of bits per color component
        if '/BitsPerComponent' in parameters:
            bits = parameters['/BitsPerComponent']
            if bits not in [1, 2, 4, 8, 16]:
                bits = 8
        else:
            bits = 8
        if '/EarlyChange' in parameters:
            earlyChange = parameters['/EarlyChange']
        else:
            earlyChange = 1
        if predictor != None and predictor != 1:
            ret = post_prediction(decoded_data, predictor, columns, colors, bits)
            return ret
        else:
            return (0, decoded_data)

def runLengthDecode(data):
    '''
           Method to decode streams using the Run-Length algorithm

           @param data: A PDF stream
           @return: A tuple (status,statusContent), where statusContent is the decoded PDF stream in case status = 0 or an error in case status = -1
       '''
    decodedStream = b''
    index = 0
    try:
        while index < len(data):
            length = data[index]
            if length >= 0 and length < 128:
                decodedStream +=bytes (data[index + 1:index + length + 2])
                index += length + 2
            elif length > 128 and length < 256:
                decodedStream += bytes(data[index + 1] * (257 - length))
                index += 2
            else:
                break
    except:
        return (-1, 'Error decoding string')
    return (0, decodedStream)

def dctDecode(data, parameters, dict_mode):
    '''
              Método para decodificar la imagen usando cuando esta ha sido codificada con el algoritmo DCTdecode

              @param data: Imagen
              @return: Una tupla (status,statusContent), donde statusContent es la imagen decodificada en caso de que status= 0
               o un error en caso de que status = -1
          '''
    decoded_data = ''
    try:
        decoded_data = data
        output = ''
    except:
        return (-1, 'Error decompressing string')

    if parameters == None or parameters == {}:
        return (0, decoded_data)
    else:
        if '/ColorTransform' in parameters:
            color_transform = parameters['/ColorTransform']
            if color_transform == 0:
                return (0, decoded_data)
            elif color_transform == 1:
                if 'mode' in dict_mode:
                    mode = dict_mode.get('mode')
                    if (mode == 'RGB'):
                        try:
                            return yuv2rgb(data).tobytes()
                        except Exception as e:
                            return (-1, 'Code error')
                    else:
                        return (-1, 'Code error')
            else:
                return ( -1, 'Code error')
        else:
            return (0, decoded_data)
        #función que extrae las imágenes de cada objeto de una página del pdf e intenta guardarla como png en la carpeta output _png

def tiff_header_for_CCITT(width, height, img_size, CCITT_group=3):
    try:
        tiff_header_struct = '<' + '2s' + 'H' + 'L' + 'H' + 'HHLL' * 8 + 'L'#'<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
        return struct.pack(tiff_header_struct,
                           b'II',  # Byte order indication: Little indian
                           42,  # Version number (always 42)
                           8,  # Offset to first IFD
                           8,  # Number of tags in IFD
                           256, 4, 1, width,  # ImageWidth, LONG, 1, width
                           257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                           258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                           259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                           262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                           273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                           278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                           279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                           0  # last IFD
                           )
    except Exception as e:
        logging.info(e)
        raise e

def tiff_decode(data, sub_obj, decode_parms = None):
    try:
        width = sub_obj['/Width']
        height = sub_obj['/Height']
        img_size = len(data)
        if decode_parms == None or decode_parms == {}:
            try:
                # lectura de las cabeceras para la compresion CCIITT
                tiff_header = tiff_header_for_CCITT(width, height, img_size)
                data = tiff_header + data
                #decodedStream = ccitt.CCITTFax().decode(data)
                return (0, data)
            except:
                return (-1, 'Error decompressing string')
        if ('/K' in decode_parms):#si existe el parametro k
            k = decode_parms.get('/K')
            if k == -1:
                CCITT_group = 4
            else:
                CCITT_group = 3
        else:
            CCITT_group = 3#por defecto K es 0 ( CCITT_group = 3)
        # lectura de las cabeceras para la compresion CCIITT
        tiff_header = tiff_header_for_CCITT(width, height, img_size, CCITT_group)
        # img_fname = "{}{:04}.tiff".format(filename_prefix, i)
        # with open(img_fname, 'wb') as img_file:
        # img_file.write(tiff_header + data)
        data = tiff_header + data
        return (0, data)
    except Exception as e:
        logging.info(e)
        raise e


def post_prediction(decoded_data, predictor, columns, colors, bits):
    '''
        Función de predicción. Obtiene el stream real (eliminando la predicción del pdf)

        @param decoded_data: imagen a decodificar
        @param predictor: el tipo de predicto a aplicar
        @param columns: numero de muestras por filas
        @param colors: numero de colores por muestras
        @param bits: numero de bits por color
        @return:  Una tupla (status,statusContent), donde statusContent es la imagen decodificada en caso de que status= 0
            o un error en caso de que status = -1
    '''
    try:
        output = b''
        bytesPerRow = (colors * bits * columns + 7) // 8

        # TIFF - 2
        # http://www.gnupdf.org/PNG_and_TIFF_Predictors_Filter#TIFF
        if predictor == 2:
            numRows = len(decoded_data) // bytesPerRow
            bitmask = 2 ** bits - 1
            outputBitsStream = b''
            for rowIndex in range(numRows):
                row = decoded_data[rowIndex * bytesPerRow:rowIndex * bytesPerRow + bytesPerRow]
                ret, colorNums = getNumsFromBytes(row, bits)
                if ret == -1:
                    return (ret, colorNums)
                pixel = [0 for x in range(colors)]
                for i in range(columns):
                    for j in range(colors):
                        diffPixel = colorNums[i + j]
                        pixel[j] = (pixel[j] + diffPixel) & bitmask
                        ret, outputBits = getBitsFromNum(pixel[j], bits)
                        if ret == -1:
                            return (ret, outputBits)
                        outputBitsStream += (outputBits)
            output = getBytesFromBits(outputBitsStream)
            return output
        # PNG prediction
        # http://www.libpng.org/pub/png/spec/1.2/PNG-Filters.html
        # http://www.gnupdf.org/PNG_and_TIFF_Predictors_Filter#TIFF
        elif predictor >= 10 and predictor <= 15:
            bytesPerRow += 1
            numRows = int((len(decoded_data) + bytesPerRow - 1) // bytesPerRow)
            numSamplesPerRow = columns + 1
            bytesPerSample = (colors * bits + 7) // 8
            upRowdata = (0,) * numSamplesPerRow
            for row in range(numRows):
                rowdata = [x for x in decoded_data[(row * int(bytesPerRow)):(row + 1) * (int(bytesPerRow))]]
                # PNG prediction can vary from row to row
                filterByte = rowdata[0]
                rowdata[0] = 0

                if filterByte == 0:
                    # None
                    pass
                elif filterByte == 1:
                    # Sub - 11
                    for i in range(1, numSamplesPerRow):
                        if i < bytesPerSample:
                            prevSample = 0
                        else:
                            prevSample = rowdata[i - bytesPerSample]
                        rowdata[i] = (rowdata[i] + prevSample) % 256
                elif filterByte == 2:
                    # Up - 12
                    for i in range(1, numSamplesPerRow):
                        upSample = upRowdata[i]
                        rowdata[i] = (rowdata[i] + upSample) % 256
                elif filterByte == 3:
                    # Average - 13
                    for i in range(1, numSamplesPerRow):
                        upSample = upRowdata[i]
                        if i < bytesPerSample:
                            prevSample = 0
                        else:
                            prevSample = rowdata[i - bytesPerSample]
                        rowdata[i] = (rowdata[i] + ((prevSample + upSample) // 2)) % 256
                elif filterByte == 4:
                    # Paeth - 14
                    for i in range(1, numSamplesPerRow):
                        upSample = upRowdata[i]
                        if i < bytesPerSample:
                            prevSample = 0
                            upPrevSample = 0
                        else:
                            prevSample = rowdata[i - bytesPerSample]
                            upPrevSample = upRowdata[i - bytesPerSample]
                        p = prevSample + upSample - upPrevSample
                        pa = abs(p - prevSample)
                        pb = abs(p - upSample)
                        pc = abs(p - upPrevSample)
                        if pa <= pb and pa <= pc:
                            nearest = prevSample
                        elif pb <= pc:
                            nearest = upSample
                        else:
                            nearest = upPrevSample
                        rowdata[i] = (rowdata[i] + nearest) % 256
                else:
                    # Optimum - 15
                    # return (-1,'Unsupported predictor')
                    pass
                upRowdata = rowdata
                try:
                    output += (bytes(rowdata[1:]))
                except Exception as e:
                    logging.info(e)
                    raise e
            return (0, output)
        else:
            return (-1, 'Wrong value for predictor')
    except Exception as e:
        logging.info(e)
        raise e
####################################################################################################################
