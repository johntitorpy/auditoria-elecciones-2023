"""
Descripcion
========================
Constantes del modulo sufragio.
"""

from msa.modulos.constants import (
    MODULO_APERTURA,
    MODULO_ASISTIDA,
    MODULO_CAPACITACION,
    MODULO_INICIO,
    MODULO_MANTENIMIENTO,
    MODULO_MENU,
    MODULO_RECUENTO,
    MODULO_SUFRAGIO,
    MODULO_TOTALIZADOR,
    MODULO_COPIAS_CERTIFICADO,
    SUBMODULO_DATOS_APERTURA,
    SUBMODULO_DATOS_ESCRUTINIO,
    SUBMODULO_MESA_Y_PIN_INICIO,
    MODULO_PRUEBA_EQUIPO,
)

MODULOS_APLICACION = [
    MODULO_APERTURA,
    MODULO_ASISTIDA,
    MODULO_CAPACITACION,
    MODULO_INICIO,
    MODULO_MANTENIMIENTO,
    MODULO_MENU,
    MODULO_RECUENTO,
    MODULO_TOTALIZADOR,
    MODULO_COPIAS_CERTIFICADO,
    MODULO_SUFRAGIO,
    SUBMODULO_MESA_Y_PIN_INICIO,
    SUBMODULO_DATOS_APERTURA,
    SUBMODULO_DATOS_ESCRUTINIO,
    MODULO_PRUEBA_EQUIPO,
]
"""
Todos los módulos de la aplicación
"""

BOTON_VOTAR_POR_CATEGORIAS = "BTN_CATEG"
"""
Representa el botón que permite votar por categorías.
"""

BOTON_LISTA_COMPLETA = "BTN_COMPLETA"
"""
Representa el botón que permite votar la lista completa.
"""

BOTON_VOTAR_EN_BLANCO = "BTN_BLANCO"
"""
Representan el botón que permite votar en blanco.
"""

PANTALLA_INSERCION_BOLETA = "insercion_boleta"
"""
Indica el nombre de la pantalla de inserción de boleta.
"""

PANTALLA_SELECCION_INTERNA = "seleccion_interna"
"""
Indica el nombre de la pantalla de selección interna.
"""

PANTALLA_SELECCION_CANDIDATOS = "seleccion_candidatos"
"""
Indica el nombre de la pantalla de selección de candidatos.
"""

PANTALLA_AGRADECIMIENTO = "agradecimiento"
"""
Indica el nombre de la pantalla de agradecimientos.
"""

PANTALLA_MENSAJE_FINAL = "mensaje_final"
"""
Indica el nombre de la pantalla de mensaje final.
"""

PANTALLA_CONSULTA = "consulta"
"""
Indica el nombre de la pantalla de consulta.
"""

PANTALLA_BOLETA_INSERTADA = "boleta_insertada"
"""
Indica el nombre de la pantalla de inserción de boletas.
"""

IDIOMAS_DISPONIBLES = (("Español", "es_AR"),)
"""
Lista con los idiomas disponibles.
"""

NUMEROS_TEMPLATES = {
    "vanilla": [2, 3, 4, 6, 8, 9, 10, 12, 15, 16, 18, 20, 24, 30, 32, 36, 40, 45],
    "empanada": [2, 3, 4, 6, 9, 12, 16, 21, 24, 30, 36],
    "soja": [8],
    "milanga": [2, 4, 6, 9, 12, 16],
    "medialuna": [2, 3, 4],
    "chipa": [2, 4, 6, 8, 9, 10, 12, 15, 18, 20, 21, 24, 30, 32, 40, 45],
}

NUMEROS_TEMPLATES_CONFIRMACION = {
    "vanilla": [1, 2, 3, 4, 5, 6, 8, 10],
    "empanada": [1, 2, 3, 4, 5, 6],
    "soja": [1, 2, 3, 4, 5, 6],
    "milanga": [1, 2, 3, 4, 5, 6],
    "medialuna": [1, 2, 3, 4, 5, 6],
    "chipa": [1, 2, 3, 4, 5, 6, 8, 10],
}

NUMEROS_TEMPLATES_VERIFICACION = {
    "chipa": [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 15],
    "empanada": [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 15],
}

"""
Por cada template, se adjunta un array con la cantidad de
casillas que se pueden habilitar y que estan soportadas.
Las mismas representan la cantidad de candidatos que se mostraran
en pantalla.
Es establecido en cada Elección.
"""

TIEMPO_POST_IMPRESION = 6000
TIEMPO_VERIFICACION = 5000
"""
Duración de tiempo para mostrar el mensaje de 
agradecimiento.
"""

TIEMPO_VERIFICACION = 5000
"""
Duración de tiempo en que la pantalla permanece
mostrando la verificación del voto.
"""

TEXTOS = (
    "conformar_voto",
    "si_confirmar_voto",
    "no_confirmar_voto",
    "votar_por_categorias",
    "votar_lista_completa",
    "su_seleccion",
    "votar_en_blanco",
    "confirmar_voto",
    "alto_contraste",
    "introduzca_boleta",
    "si_tiene_dudas",
    "su_voto_impreso",
    "muchas_gracias",
    "puede_retirar_boleta",
    "si_desea_verificarla",
    "imprimiendo_voto",
    "no_retirar_boleta",
    "agradecimiento",
    "este_es_su_voto",
    "volver_al_inicio",
    "aguarde_unos_minutos",
    "seleccionar_idioma",
    "aceptar",
    "cancelar",
    "confirmar_seleccion",
    "cargando_interfaz",
    "espere_por_favor",
    "no_olvide_verificar",
    "palabra_lista",
    "sus_candidatos",
    "candidato_no_seleccionado",
    "verificando_seleccion",
    "cambiar_modo_votacion",
    "salir_al_menu",
    "seleccione_accion",
    "error_grabar_boleta_alerta",
    "error_grabar_boleta_aclaracion",
    "si_desea_verificarla_alto_cotraste",
    "cinta_capacitacion",
    "cinta_demostracion",
    "modificar",
    "palabra_no_presenta_candidatos",
    "papel_no_insertado_ok",
    "palabra_siguiente",
    "palabra_orden",
)

"""
Textos que se utilizan para mostrar mensajes en las
pantallas.
"""

TEMPLATES_FLAVORS = {
    "common": (
        "categoria",
        "lista",
        "partido",
        "consulta_popular",
        "confirmacion",
        "confirmacion_tarjeta",
        "confirmacion_candidato_blanco",
        "candidatos_adicionales",
        "candidato_hijo",
        "colores",
        "solapa",
        "boleta_header",
        "boleta_verificador",
        "boleta_watermark",
        "boleta_troquel",
        "boleta_tarjeta_voto_blanco",
        "boleta_tarjeta_con_preferencias",
        "boleta_tarjeta_sin_preferencias",
        "boleta_tarjeta_con_secundarios",
        "boleta_tarjeta_con_suplentes",
        "boleta_tarjeta_con_secundarios_y_suplentes",
    ),
    "vanilla": (
        "candidato_categoria",
        "candidato_verificacion",
        "confirmacion_consulta_popular",
        "confirmacion_candidato_elegido",
    ),
    "empanada": (
        "candidato_categoria",
        "candidato_para_categoria",
        "candidato_verificacion",
        "seleccion_adhesion",
        "seleccion_lista_completa",
        "confirmacion_consulta_popular",
        "confirmacion_candidato_elegido",
    ),
    "chipa": (
        "candidato",
        "candidato_blanco",
        "candidato_con_secundarios",
        "candidato_lista_con_imagen",
        "candidato_pre_vice_con_imagen",
        "candidato_lista_sin_imagen",
        "candidato_verificacion_blanco",
        "candidato_verificacion_foto_izquierda",
        "candidato_verificacion_con_secundarios",
        "candidato_verificacion_con_secundarios_foto_izquierda",
        "confirmacion_con_secundarios",
        "confirmacion_pre_vice",
        "confirmacion_con_secundarios_y_preferentes",
        "confirmacion_con_preferentes",
        "verificacion_tarjeta",
        "verificacion_con_secundarios",
        "verificacion_con_secundarios_y_preferentes",
        "verificacion_con_preferentes",
        "verificacion_cerrada",
        "verificacion_candidato_blanco",
        "verificacion_pre_vice",
        "tachas",
        "preferencias",
        "colores",
    ),
    "centolla": (),
    "soja": (),
    "milanga": (),
    "medialuna": (),
}
