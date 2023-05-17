# -*- coding: utf-8 -*-
from __future__ import absolute_import
from msa.core.packing.numpacker import pack_slow, unpack_slow
import six


def encodear_string_apertura(string):
    string = six.text_type(string.upper())
    datos = []
    letra = None
    for char in string:
        codigo_letra = ord(char)
        if 65 <= codigo_letra <= 90:
            letra = codigo_letra - 64
        elif char == "'":
            letra = 28
        elif char == u"Ñ":
            letra = 29
        elif char == " ":
            letra = 30
        elif char == u"Á":
            letra = 1
        elif char == u"É":
            letra = 5
        elif char == u"Í":
            letra = 9
        elif char == u"Ó":
            letra = 15
        elif char == u"Ú":
            letra = 21
        elif char == u";":
            letra = 31

        if letra is not None:
            datos.append(letra)

    ret = pack_slow(datos, 5)
    return ret


def decodear_string_apertura(array_datos):
    ret = u""
    string_datos = b''
    for elem in array_datos:
        string_datos += elem

    datos = unpack_slow(string_datos, 5)
    for codigo_letra in datos:
        letra = None
        # A-Z
        if 1 <= codigo_letra <= 27:
            letra = chr(codigo_letra + 64)
        # '
        elif codigo_letra == 28:
            letra = u"'"
        # Ñ
        elif codigo_letra == 29:
            letra = u"Ñ"
        # Espacio
        elif codigo_letra == 30:
            letra = u" "
        elif codigo_letra == 31:
            letra = ";"
        if letra is not None:
            ret += letra
    return ret


def smart_title(string):
    """Tituliza un string sin tener en cuenta ciertas palabras
    (ex. preposiciones, etc.)."""
    EXCEPCIONES = ('a', 'ante', 'bajo', 'con', 'contra', 'de', 'desde', 'del',
                   'durante', 'e', 'en', 'entre', 'hacia', 'hasta', 'mediante',
                   'y', 'para', 'por', 'según', 'segun', 'sin', 'so', 'sobre',
                   'tras', 'versus', 'via', 'la', 'los')
    SIGLAS = ('ti', 'mst', 'eco', 'pro', '(aps)', '(aupec)', '(mst)',
              'ucr', 'unen', 'ps')
    # Primero titulizamos el string
    titleized = string.title()
    splitted = titleized.split(' ')
    result = []
    # Chequeamos si hay algo que esté en la lista de excepciones
    for t in splitted:
        if t.lower() in EXCEPCIONES and splitted.index(t) != 0:
            result.append(t.lower())
        elif t.lower() in SIGLAS:
            result.append(t.upper())
        else:
            result.append(t)

    return ' '.join(result)
