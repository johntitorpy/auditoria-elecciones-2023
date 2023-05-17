"""Constants del modulo escrutinio."""
from collections import OrderedDict
from msa.core.armve.constants import PRINT_HIGH, PRINT_LOW, PRINT_MID, PRINT_SHIGH, PRINT_SLOW
from msa.core.documentos.constants import (CIERRE_ESCRUTINIO, CIERRE_RECUENTO,
                                           CIERRE_TRANSMISION, CIERRE_PREFERENCIAS, CIERRE_COPIA_FIEL,
                                           CIERRE_CERTIFICADO)

SECUENCIA_CERTIFICADOS = [CIERRE_RECUENTO, CIERRE_TRANSMISION,
                          CIERRE_ESCRUTINIO]


SECUENCIA_CERTIFICADOS = {
    "default": [CIERRE_RECUENTO, CIERRE_TRANSMISION, CIERRE_ESCRUTINIO],
    "trep": [CIERRE_TRANSMISION, CIERRE_RECUENTO, CIERRE_RECUENTO, CIERRE_RECUENTO, CIERRE_ESCRUTINIO]
}

TIPO_ACTAS = {
    'con_chip': {
        'default': [CIERRE_RECUENTO, CIERRE_TRANSMISION],
        'trep': [CIERRE_TRANSMISION, CIERRE_PREFERENCIAS]
    },
    'sin_chip': {
        'default': [CIERRE_ESCRUTINIO, CIERRE_COPIA_FIEL, CIERRE_CERTIFICADO],
        'trep': [CIERRE_ESCRUTINIO, CIERRE_COPIA_FIEL, CIERRE_CERTIFICADO, CIERRE_RECUENTO]
    }
}

"""
Secuencia en la que los certificados deben ser procesados.
"""

MINIMO_BOLETAS_RECUENTO = 10
"""
Mínimo de boletas que debe tener cada recuento, para mostrar alerta en caso
contrario
"""

ACT_INICIAL = 0
"""
Codificación para determinar que es la boleta inicial
"""

ACT_BOLETA_NUEVA = 1
"""
Codificación para determinar que la boleta es nueva
"""

ACT_BOLETA_REPETIDA = 2
"""
Codificación para determinar que la boleta esta repetida.
"""

ACT_ERROR = 3
"""
Codificación para determinar un error con el acta.
"""

ACT_ESPECIALES = 4
"""
Codificación para determinar actas especiales.
"""

ACT_VERIFICAR_ACTA = 5
"""
Codificación para determinar la verificación del acta.
"""

PRINTER_QUALITY_MAP = OrderedDict({
    'PRINT_SLOW':   PRINT_SLOW,
    'PRINT_LOW':    PRINT_LOW,
    'PRINT_MID':    PRINT_MID,
    'PRINT_HIGH':   PRINT_HIGH,
    'PRINT_SHIGH':  PRINT_SHIGH
})


TEXTOS = (
    "cargando_interfaz", "espere_por_favor", "boletas_procesadas",
    "bienvenida_recuento", "boleta_repetida", "error_lectura",
    "finalizar_recuento", "aceptar", "cancelar", "seguro_salir_escrutinio",
    "seguro_salir_escrutinio_aclaracion", "pocas_boletas_alerta",
    "pocas_boletas_pregunta", "pocas_boletas_aclaracion", "total_general",
    "fin_escrutinio_pregunta", "fin_escrutinio_aclaracion", "volver",
    "introduzca_acta_cierre", "introduzca_acta_transmision",
    "palabra_siguiente", "recuento_no_almacenado_alerta",
    "palabra_anterior", "palabra_finalizar", "imprimir_actas",
    "recuento_no_almacenado_aclaracion", "mensaje_imprimiendo",
    "transmision_no_almacenada_alerta", "imprimiendo_acta",
    "transmision_no_almacenada_aclaracion", "continuar_recuento",
    "certificado_no_impreso_alerta", "certificado_no_impreso_aclaracion",
    "introduzca_acta_escrutinio", "introduzca_acta_recuento",
    "asegurese_firmar_acta", "el_suplente_acercara", "usted_puede_imprimir",
    "fiscales_qr", "introduzca_certificado_boletas", "palabra_lista",
    "introduzca_sobre_actas", "introduzca_certificados_para_fiscales",
    "lista_actas_sobre", "lista_otras_actas", "padrones_electorales",
    "otros_votos", "poderes_fiscales", "certificado_de_escrutinio",
    "boletas_votos_nulos", "introducir_urna", "cerrar_faja_seguridad",
    "palabra_siguiente", "mensaje_copias", "mensaje_copias_recuento",
    "mensaje_copias_escrutinio", "seguro_salir_totalizador",
    "finalizar_totalizacion", "bienvenida_totalizador", "acta_repetida",
    "continuar_totalizacion", "apagar", "titulo_confirmacion_apagado",
    "recuerde_remover_disco", "verificar_acta", "revisar_acta_totalizador",
    "fin_totalizacion_pregunta", "fin_totalizacion_aclaracion",
    "actas_procesadas", "introduzca_acta_preferencias", "error_max_boletas",
    "continuar_recuento_max_boletas", "palabra_orden"
)

TARJETAS_CANDIDATO_NUMEROS_TEMPLATES = [1, 2, 3, 4, 5, 6, 8, 10]

TEMPLATES_FLAVORS = {
    "common": (
        "escrutinio_confirmacion_blanco",
        "boleta_header", "boleta_verificador",
        "boleta_watermark", "boleta_troquel",
        "boleta_tarjeta_voto_blanco",
        "boleta_tarjeta_con_preferencias", "boleta_tarjeta_sin_preferencias",
        "boleta_tarjeta_con_secundarios", "boleta_tarjeta_con_suplentes",
        "boleta_tarjeta_con_secundarios_y_suplentes",
    ),
    "vanilla": (
        "escrutinio_confirmacion_candidato",
        "escrutinio_confirmacion_consulta_popular",
    ),
    "empanada": (
        "escrutinio_confirmacion_candidato",
        "escrutinio_confirmacion_consulta_popular",
    ),
    "chipa": (
        "escrutinio_confirmacion_pre_vice",
        "escrutinio_confirmacion_con_secundarios",
        "escrutinio_confirmacion_con_secundarios_y_preferentes",
        "escrutinio_confirmacion_con_preferentes",
        "escrutinio_confirmacion_sin_preferentes",
        "encabezado_chico"
    ),
    "centolla": (),
    "soja": (),
    "milanga": (),
    "medialuna": (),
}
