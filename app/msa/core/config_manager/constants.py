from msa.core.data.settings import JUEGO_DE_DATOS
from msa.constants import PATH_VARS
from os.path import join, exists

COMMON_SETTINGS = "common"
DEFAULT_FILE = "default"
OVERRIDE_FILE = "local"
EXTENSION = "yml"

PATH_CONFIGS = join(PATH_VARS, 'config', 'default')
if exists(join(PATH_VARS, 'config', JUEGO_DE_DATOS)):
    PATH_CONFIGS = join(PATH_VARS, 'config', JUEGO_DE_DATOS)

try:
    from msa.core.config_manager.settings_local import *
except ImportError:
    pass
