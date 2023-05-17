# -*- coding:utf-8 -*-
"""
Descripcion
===============================

Establece settings generales del sistema

"""
#: Para establecer si se deben imprimir logs de debug
DEBUG = False
#: Indica si nos encontramos en modo demo. Se usa para capacitacion.
MODO_DEMO = False
#: Indica si las celdas de los tags se deben marcar como read_only al grabarlos.
QUEMA = True

try:
    from msa.settings_local import *
except ImportError:
    pass
