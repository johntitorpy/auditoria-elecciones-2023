from os.path import join

from msa.constants import PATH_VARS


PATH_KEYS = join(PATH_VARS, 'keys')

NOMBRE_KEY_TECNICO = "tecnico"
NOMBRE_KEY_AUTORIDAD = "autoridad"
NOMBRE_KEY_TRANSMISION = "transmision"

PADDING_SERIAL = b"\x00\x00\x00\x00"
DERIVACIONES = 1000000
