# -*- coding: utf-8 -*-
from __future__ import absolute_import

USAR_PIR = True
USAR_PORTS = False
USAR_PRESENCIA = True
USAR_FAN = True
ITERACIONES_APAGADO = 12

# Brillo en armve
DEFAULT_BRIGHTNESS = 100

# Potencia de la antena (armve). Full (255)/Half (0)
RFID_POWER = 0

try:
    from msa.core.hardware.settings_local import *
except ImportError:
    pass
