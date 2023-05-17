# -*- coding: utf-8 -*-

""" Módulo para codificar las actas de forma tal que se puedan almacenar en un
chip de 1K

"""
from __future__ import absolute_import
from six.moves import range
import zlib

# Es el tamaño máximo en bits que se puede codificar antes de pasar al
# próximo modo
MAXBITS = 2464
# Tamaño en bits de la posición de la parte más significativa
POSBITS = 12

# Cantidad de bits para representar el número que indica 
# con cuantos bits se usan para representar los datos
# Ejemplo:
#       META_DATABITS = 4 , entonces:
#           1.  Puedo almacenar numeros en el rango [0,15]
#           2.  Si en este campo almaceno el numero 15, entonces
#               voy a usar 15 bits para represantar los votos de cada lista/candidato 
#               del recuento
#           3.  Quiere decir que puedo almacenar hasta (2^15) - 1 votos = 32767 
#               por cada candidatura, es decir, podría tener 32767 electores habilitados por mesa.
#       

META_DATABITS = 4

# Es el diccionario que indica cuantos bits (valor) necesitaría para representar 
# un numero (key). Se generan hasta 2^META_DATABITS entradas, porque es lo maximo 
# que me permite ese parámetro.
DATABITS_MAX = {x: (2**x)-1 for x in range(1, 2**META_DATABITS)}

# Tamaño del identificador de modo
MODOBITS = 3

# Diccionario para determinar cantidad de bits fijos y variables según 
# el valor de META_DATABITS y MODOBITS
BITSMODO = {x: { y: [(y+1) if (y+1)<= x else x, x-(y+1) if (x-(y+1)) >= 0 else 0] for y in range(2**MODOBITS)} for x in range(1, 2**META_DATABITS)}

# Tamaño máximo para la lista de datos
MAXDATOS = (2**POSBITS) - 1
# Offset mesa. Las mesas comienzan en 1001, por lo que se almacena la
# diferencia respecto al offset
OFFSETMESA = 0

# Cantidad de bits para almacenar el nro de mesa
BITS_NUMERO_MESA = 17


def nro2cod(nro, bits_fijos, bits_variables, posicion):
    """ Codifica el nro devolviendo una tupla con la parte fija y la
        variable respectivamente.

        Si hay parte variable, la devuelve con la posicion que se pasa

    Tomo la parte menos significativa haciendo un and bit por bit por la
    mascara.

    Ej: bits_fijos=4 bits_variables=5 nro=173

    masc_menor_signif = 0b000001111 = 2 ** 4 - 1
                  nro = 0b010101101 = 173
    menor_signif      = 0b000001101 = 13


    Aplico en and y divido por 2 ** 4 para sacar la parte menos
    significativa (equivale a mayor_signif >> 4)

    masc_mayor_signif = 0b111110000 = 2 ** 9 - 2 ** 4
                  nro = 0b010101101 = 173
    mayor_signif      = 0b010100000 = 160
                      = 0b010100000 / 0b10000 = 160 / 2 ** 4 = 0b01010
    """
    masc_menor_signif = 2 ** bits_fijos - 1
    masc_mayor_signif = 2 ** (bits_fijos + bits_variables) - 2 ** bits_fijos

    menor_signif = nro & masc_menor_signif
    mayor_signif = int((nro & masc_mayor_signif) / 2 ** bits_fijos)

    if nro > (masc_mayor_signif | masc_menor_signif):
        raise ValueError("Imposible empaquetar nro=%s" % nro)

    parte_fija = bin(menor_signif)[2:].zfill(bits_fijos)

    parte_variable = None
    if mayor_signif > 0:
        # Agrego la posicion como POSBITS bits
        pos = bin(posicion)[2:].zfill(POSBITS)
        parte_variable = "%s%s" % (pos,
                                   bin(mayor_signif)[2:].zfill(bits_variables))

    return (parte_fija, parte_variable)


def binstr2strbytes(binstr):
    """ Convierte una cadena con binarios en un string de bytes que son
        representados por dicha cadena

        Ej: binstr2strbytes('010000110100101001000100') = 'CJD'
    """
    # Completo el string para que la longitud sea multiplo de 8
    if len(binstr) % 8 != 0:
        binstr = binstr + "0" * (8 - len(binstr) % 8)

    strbytes = b""
    for i in range(0, len(binstr), 8):
        _byte = binstr[i:i + 8]
        strbytes = strbytes + bytes([int(_byte, 2)])

    return strbytes


def strbytes2binstr(strbytes):
    """ Convierte un string de bytes en una cadena de binarios

        Ej: strbytes2binstr('PIGU') = ???
    """
    binstr = ""
    for c in strbytes:
        binstr = binstr + bin(c)[2:].zfill(8)

    return binstr


def bitsfijos(databits, modo):
    """ Devuelve la cantidad de bits fijos que tiene el modo indicado según
        los databits usados
    """
    modos = BITSMODO[databits]
    if modo in modos:
        return modos[modo][0]
    else:
        msg = "Modo {} no válido. Se admiten solamente los modos 0-{}".format(modo, 2**MODOBITS)
        raise LookupError(msg)


def bitsvariables(databits, modo):
    """ Devuelve la cantidad de bits variables que tiene el modo indicado según
        los databits usados
    """
    modos = BITSMODO[databits]
    if modo in modos:
        return modos[modo][1]
    else:
        msg = "Modo {} no válido. Se admiten solamente los modos 0-{}".format(modo, 2**MODOBITS)
        raise LookupError(msg)

def detectar_data_bits(datos):
    maximo_valor_a_representar = max(datos)
    for bits, maximo_valor_posible in DATABITS_MAX.items():
        if maximo_valor_posible >= maximo_valor_a_representar:
            return bits

def _pack(mesa, datos, modo=0):
    """ Codifica los datos enviados como lista de enteros

        Va a codificar los valores enteros con un ancho fijo dado por el
        modo. Los valores que necesiten mas digitos binarios se agregan al
        final con el formato id (POSBITS bits, es el orden en la lista) +los
        digitos mas significativos que requiere.
    """

    # Chequeos de sanidad:
    if len(datos) >= MAXDATOS:
        raise AssertionError("La cant. de datos a empaquetar supera al máximo")
    if (mesa - OFFSETMESA) >= 2 ** BITS_NUMERO_MESA:
        raise AssertionError("El número de mesa supera al máximo")

    # Detecta la cantidad de bits a usar segun
    # el mayor numero que debo representar
    numero_data_bits = detectar_data_bits(datos)
    
    # Obtiene la cantidad de bits por modo
    bits_fijos = bitsfijos(numero_data_bits, modo)
    bits_var = bitsvariables(numero_data_bits, modo)
    
    binmesa = bin(mesa - OFFSETMESA)[2:].zfill(BITS_NUMERO_MESA)
    binmodo = bin(modo)[2:].zfill(MODOBITS)
    bin_numero_data_bits = bin(numero_data_bits)[2:].zfill(META_DATABITS)
    bincantdatos = bin(len(datos))[2:].zfill(POSBITS)

    prefijo = "%s%s%s%s" % (binmesa, binmodo, bin_numero_data_bits, bincantdatos)
    parte_fija = ""
    parte_variable = ""

    pos = 0
    for nro in datos:
        nrocod = nro2cod(nro, bits_fijos, bits_var, pos)
        parte_fija = parte_fija + nrocod[0]

        # Agrego a la parte variable si tiene parte variable
        if nrocod[1] is not None:
            parte_variable = parte_variable + nrocod[1]
        pos += 1

    strbytes = binstr2strbytes(prefijo + parte_fija + parte_variable)

    strbytes = zlib.compress(strbytes)

    return strbytes

def pack(mesa: int, datos: 'list[int]', max_bits = MAXBITS) -> bytes:

    # Si la longitud del string generado es mayor al soportado prueba con
    # el siguiente modo. Si el modo supera 3, devuelve una excepción

    # Empaquetar en todos los modos, para determinar cual es el óptimo:
    strbytes = min([_pack(mesa, datos, modo) for modo in range(2**MODOBITS)], key=len)

    if len(strbytes) * 8 > max_bits:
        msg = "La codif en todos los modos superan la long max de %d bits"
        raise OverflowError(msg % max_bits)
    else:
        return strbytes


def unpack(strbytes):
    """ Decodifica los datos enviados como string de bytes

        Va a devolver una tupla con el número de mesa y la lista de valores
    """
    strbytes = zlib.decompress(strbytes)
    binstr = strbytes2binstr(strbytes)

    # La mesa ocupa los primeros BITS_NUMERO_MESA bits. Tiene un offset de
    # OFFSETMESA por lo que se le suman

    mesa = int(binstr[0:BITS_NUMERO_MESA], 2) + OFFSETMESA
    # El modo ocupa los MODOBITS bits siguientes
    modo = int(binstr[BITS_NUMERO_MESA:BITS_NUMERO_MESA + MODOBITS], 2)
    # El numero_data_bits ocupa los META_DATABITS bits siguientes
    numero_data_bits = int(binstr[BITS_NUMERO_MESA + MODOBITS:BITS_NUMERO_MESA + MODOBITS + META_DATABITS], 2)
    # La cantidad de datos ocupa los POSBITS bits siguientes
    cant_datos = int(binstr[BITS_NUMERO_MESA + MODOBITS + META_DATABITS:BITS_NUMERO_MESA + MODOBITS + META_DATABITS + POSBITS], 2)

    # Obtiene la cantidad de bits segun el modo
    bits_fijos = bitsfijos(numero_data_bits, modo)
    bits_var = bitsvariables(numero_data_bits, modo)

    # Los datos ocupan los siguientes bits
    bindatos = binstr[BITS_NUMERO_MESA + MODOBITS + META_DATABITS + POSBITS:BITS_NUMERO_MESA + MODOBITS + META_DATABITS + POSBITS + cant_datos * bits_fijos]

    datos = []
    for i in range(0, len(bindatos), bits_fijos):
        bindato = bindatos[i:i + bits_fijos]
        datos.append(int(bindato, 2))
    
    # A partir de eso vienen los datos variables es decir la direccion mas
    # los bits significativos de aquellos que los requieren
    bindatosvariables = binstr[BITS_NUMERO_MESA + MODOBITS + META_DATABITS + POSBITS + cant_datos * bits_fijos:]
    # Omito los 0 que se agregaron para completar el byte
    longitud_ajustada = int(len(bindatosvariables) / (POSBITS + bits_var)) * \
                            (POSBITS + bits_var)
    bindatosvariables = bindatosvariables[:longitud_ajustada]
    
    for i in range(0, len(bindatosvariables), POSBITS + bits_var):
        bindatovariable = bindatosvariables[i:i + POSBITS + bits_var]
        pos = int(bindatovariable[0:POSBITS], 2)
        valor = int(bindatovariable[POSBITS:], 2) * (2 ** bits_fijos)
        datos[pos] = datos[pos] + valor

    return (mesa, datos)
