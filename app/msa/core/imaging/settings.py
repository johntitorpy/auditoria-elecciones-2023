from msa.core.documentos.constants import CIERRE_TRANSMISION
from os.path import join
from msa.core.data.settings import JUEGO_DE_DATOS
from msa.constants import PATH_VARS

PATH_TEMPLATE = join(PATH_VARS, 'datos', JUEGO_DE_DATOS)
PATH_TEMPLATE_IMPRESION = join(PATH_TEMPLATE, 'TemplatesImpresion.json')
PATH_TEMPLATE_MAP = join(PATH_TEMPLATE, 'TemplatesMap.json')
PATH_TMP = '/tmp/'

ACTAS_CON_CTX = [CIERRE_TRANSMISION]

X_BASE = 66
Y_BASE = 86

PIXEL = 3
