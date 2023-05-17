"""
Descripcion
========================
Contiene las constantes que se usan en los modulos.
Define:
    - Constantes para los nombres de los modulos del sistema.
    - Path a los directorios de recursos como templates, flavors, sonidos,etc.
    - Estados de la rampa.

Varios
-------------------------
.. data:: PATH_RECURSOS_VOTO
.. data:: PATH_FOTOS_ORIGINALES
.. data:: PATH_MODULOS
.. data:: PATH_TEMPLATES_MODULOS
.. data:: PATH_TEMPLATES_VAR
.. data:: PATH_TEMPLATES_FLAVORS
.. data:: PATH_SONIDOS_VOTO

.. _modulos.constants.mods_y_submods:

Modulos y submodulos
-------------------------

.. data:: MODULO_APERTURA
.. data:: MODULO_ASISTIDA
.. data:: MODULO_CALIBRADOR
.. data:: MODULO_CAPACITACION
.. data:: MODULO_INICIO
.. data:: MODULO_MANTENIMIENTO
.. data:: MODULO_MENU
.. data:: MODULO_RECUENTO
.. data:: MODULO_SUFRAGIO
.. data:: MODULO_TOTALIZADOR
.. data:: MODULO_INGRESO_DATOS
.. data:: SUBMODULO_DATOS_APERTURA
.. data:: SUBMODULO_DATOS_ESCRUTINIO
.. data:: SUBMODULO_MESA_Y_PIN_INICIO
.. data:: MODULOS_PLUGINS

Estados
-------------------------

Comunes
~~~~~~~~~~~~~~~~~~~~~~~

.. data:: E_ESPERANDO
.. data:: E_ESPERANDO_TAG
.. data:: E_EXPULSANDO_BOLETA
.. data:: E_INICIAL

Voto
~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: E_VOTANDO
.. data:: E_CONSULTANDO
.. data:: E_CONSULTANDO_CON_PAPEL
.. data:: E_REGISTRANDO

Apertura
~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: E_CARGA 
.. data:: E_CONFIRMACION 

Inicio
~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: E_EN_CONFIGURACION 
.. data:: E_CONFIGURADA 

Rrecuento
~~~~~~~~~~~~~~~~~~~~~~~~
.. data:: E_SETUP 
.. data:: E_RECUENTO 
.. data:: E_CLASIFICACION 
.. data:: E_RESULTADO 
.. data:: E_VERIFICACION 
.. data:: E_IMPRIMIENDO 

Ingreso de datos
~~~~~~~~~~~~~~~~~~~~~~~~
.. data:: E_INGRESO_ACTA 
.. data:: E_MESAYPIN 
.. data:: E_INGRESO_DATOS 

"""

from os.path import join
from msa.constants import PATH_RECURSOS, PATH_CODIGO, PATH_VARS


FONT_NAME = "Nimbus Sans L"

try:
    import gi

    gi.require_version("Pango", "1.0")
    from gi.repository import Pango

    DEFAULT_FONT = Pango.FontDescription(FONT_NAME)
except ImportError:
    DEFAULT_FONT = None

PATH_RECURSOS_VOTO = join(PATH_RECURSOS, "voto")
PATH_FOTOS_ORIGINALES = join(PATH_VARS, "imagenes_candidaturas")
PATH_MODULOS = join(PATH_CODIGO, "modulos")
PATH_TEMPLATES_MODULOS = join(PATH_MODULOS, "gui", "templates")
PATH_TEMPLATES_VAR = join(PATH_VARS, "modulos", "templates")
PATH_TEMPLATES_FLAVORS = join(PATH_TEMPLATES_VAR, "flavors")
PATH_TEMPLATES_GUI = join(PATH_MODULOS, "gui", "templates")
PATH_SONIDOS_VOTO = join(PATH_MODULOS, "gui", "sonidos")

EXT_IMG_VOTO = "webp"
FLAVORS_HABILITADOS = ["chipa"]

MODULO_APERTURA = "apertura"
MODULO_ASISTIDA = "asistida"
MODULO_CALIBRADOR = "calibrador"
MODULO_CAPACITACION = "capacitacion"
MODULO_INICIO = "inicio"
MODULO_MANTENIMIENTO = "mantenimiento"
MODULO_MENU = "menu"
MODULO_RECUENTO = "escrutinio"
MODULO_SUFRAGIO = "sufragio"
MODULO_TOTALIZADOR = "totalizador"
MODULO_INGRESO_DATOS = "ingreso_datos"
MODULO_COPIAS_CERTIFICADO = "copias_certificado"
MODULO_PRUEBA_EQUIPO = "prueba_equipo"

SUBMODULO_DATOS_APERTURA = ",".join((MODULO_INGRESO_DATOS, MODULO_APERTURA))
SUBMODULO_DATOS_ESCRUTINIO = ",".join((MODULO_INGRESO_DATOS, MODULO_RECUENTO))
SUBMODULO_MESA_Y_PIN_INICIO = ",".join((MODULO_INGRESO_DATOS, MODULO_INICIO))

MODULOS_PLUGINS = [MODULO_TOTALIZADOR]

#: Usado para apagar la máquina
SHUTDOWN = "shutdown"

COMANDO_EXPULSION_CD = "eject /dev/sr0 -i off; eject /dev/sr0"
COMANDO_APAGADO = "/sbin/poweroff"

WINDOW_BORDER_WIDTH = 12
APP_TITLE = "Sistema de la Boleta Única Electrónica"

# ESTADOS DE LA RAMPA

# COMUNES
E_ESPERANDO = "ESPERANDO"
E_ESPERANDO_TAG = "ESPERANDO_TAG"
E_EXPULSANDO_BOLETA = "EXPULSANDO_BOLETA"
E_INICIAL = "INICIAL"

# VOTO
E_VOTANDO = "VOTANDO"
E_CONSULTANDO = "CONSULTANDO"
E_CONSULTANDO_CON_PAPEL = "CONSULTANDO_CON_PAPEL"
E_REGISTRANDO = "REGISTRANDO"

# APERTURA
E_CARGA = "CARGA"
E_CONFIRMACION = "CONFIRMACION"

# INICIO
E_EN_CONFIGURACION = "EN_CONFIGURACION"
E_CONFIGURADA = "CONFIGURADA"

# RECUENTO
E_SETUP = "SETUP"
E_RECUENTO = "RECUENTO"
E_CLASIFICACION = "CLASIFICACION"
E_RESULTADO = "RESULTADO"
E_VERIFICACION = "VERIFICACION"
E_IMPRIMIENDO = "IMPRIMIENDO"

# INGRESO_DATOS
E_INGRESO_ACTA = "ESPERANDO_INGRESO_ACTA"
E_MESAYPIN = "INGRESO_MESA_Y_PIN"
E_ID_MESA_Y_PIN = "INGRESO_ID_MESA_Y_PIN"
E_INGRESO_DATOS = "INGRESO_DATOS_AUTORIDADES"

CHECK_READ_ONLY = False
