# -*- coding: utf-8 -*-

# settings para rfid
TOKEN = 'E8'
TOKEN_TECNICO = '73'
COMPROBAR_TOKEN = True

# cosas de impresion
COMPRESION_IMPRESION = False
USAR_BUFFER_IMPRESION = False

try:
    from msa.core.settings_local import *
except ImportError as e:
    pass
