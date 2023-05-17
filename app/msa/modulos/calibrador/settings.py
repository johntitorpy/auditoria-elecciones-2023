"""Settings para el calibrador."""
TEST = False
FAKE_DEV = False

DEBUG = False

TH_MISCLICK = 30
TH_DUALCLICK = 100
TH_ERRORES = 6

INIT_LIBINPUT_PROP_VALUES = [1, 0, 0, 0, 1, 0, 0, 0, 1]

try:
    from msa.modulos.calibrador.settings_local import *
except ImportError:
    pass