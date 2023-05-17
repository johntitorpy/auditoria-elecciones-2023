from msa.core.armve.constants import (LED_ENTRY, LED_EXIT, LED_ANTENNA,
                                      LED_AUDIO, LED_ALLIN,
                                      BLACK, RED, GREEN, BLUE, YELLOW,
                                      MAGENTA, CYAN, WHITE, VIOLET, ORANGE,
                                      INDIGO, SEESAW_LOW, SEESAW_MEDIUM, SEESAW_HIGH)

FIXED = 0
BLINK = 1
SEESAW = 2
BLINK_TWO_COLORS = 3
SEESAW_SPEED = SEESAW_MEDIUM
LED_PERIOD = 300  # Blinking frequency(ms)
PREVIOUS_LED_ACTION = 'previous_led_action'

# LED_TIMEOUT = 5000 #Blinking total time(segs)

ACTIONS = {
    'reset': [
        {'id_led': LED_ALLIN, 'color': BLACK, 'behavior': FIXED, 'timeout': 0}],
    'menu': [
        {'id_led': LED_ALLIN, 'color': RED, 'behavior': FIXED, 'timeout': 0}],
    'pantalla_espera_sufragio': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0},
        {'id_led': LED_ANTENNA, 'color': WHITE, 'behavior': SEESAW, 'timeout': 0}],
    'boleta_en_rampa': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': FIXED, 'timeout': 0}],
    'impresion': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': FIXED, 'timeout': 0},
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0}],
    'impresion_mantenimiento': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': FIXED, 'timeout': 3000},
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': SEESAW, 'timeout': 3000}],
    'expulsar_boleta': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': FIXED, 'timeout': 2000},
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': BLINK, 'timeout': 2000}],
    'error_impresion': [
        {'id_led': LED_ENTRY, 'color': RED, 'behavior': FIXED, 'timeout': 2000},
        {'id_led': LED_EXIT, 'color': RED, 'behavior': SEESAW, 'timeout': 2000}],
    'verificacion_post_impresion': [
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': FIXED, 'timeout': 0},
        {'id_led': LED_ANTENNA, 'color': WHITE, 'behavior': SEESAW, 'timeout': 0}],
    'solicitud_acta': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0}],
    'fin_impresion': [
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'espera_en_antena': [
        {'id_led': LED_ANTENNA, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0}],
    'error_lectura_antena': [
        {'id_led': LED_ANTENNA, 'color': RED, 'behavior': FIXED, 'timeout': 600}],
    'ok_lectura_antena': [
        {'id_led': LED_ANTENNA, 'color': GREEN, 'behavior': FIXED, 'timeout': 600}],
    'error_boleta_a_expulsar': [
        {'id_led': LED_ENTRY, 'color': RED, 'behavior': FIXED, 'timeout': 600}],
    'error_boleta_a_expulsar_2': [
        {'id_led': LED_ENTRY, 'color': RED, 'behavior': BLINK, 'timeout': 1000}],
    'lectura_ok': [
        {'id_led': LED_ALLIN, 'color': GREEN, 'behavior': FIXED, 'timeout': 600}],
    'lectura_repetida': [
        {'id_led': LED_ALLIN, 'color': YELLOW, 'behavior': FIXED, 'timeout': 600}],
    'lectura_error': [
        {'id_led': LED_ALLIN, 'color': RED, 'behavior': FIXED, 'timeout': 600}],
    'pedir_acta': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'ingreso_datos': [
        {'id_led': LED_ALLIN, 'color': MAGENTA, 'behavior': SEESAW, 'timeout': 0}],
    'pedir_acta_asistida': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': BLINK, 'timeout': 0},
        {'id_led': LED_AUDIO, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'espera_asistida': [
        {'id_led': LED_AUDIO, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'impresion_asistida': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': FIXED, 'timeout': 0},
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': BLINK, 'timeout': 0},
        {'id_led': LED_AUDIO, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'fin_impresion_asistida': [
        {'id_led': LED_EXIT, 'color': CYAN, 'behavior': BLINK, 'timeout': 0},
        {'id_led': LED_AUDIO, 'color': CYAN, 'behavior': BLINK, 'timeout': 0}],
    'verificacion_post_impresion_asistida': [
        {'id_led': LED_ENTRY, 'color': GREEN, 'behavior': BLINK, 'timeout': 0}],
    'suspension': [
        {'id_led': LED_ENTRY, 'color': BLUE, 'behavior': SEESAW, 'timeout': 0},
        {'id_led': LED_ANTENNA, 'color': BLUE, 'behavior': SEESAW, 'timeout': 0}],
    'alerta_salida_escrutinio': [
        {'id_led': LED_ALLIN, 'color': ORANGE, 'color2': BLUE, 'behavior': BLINK_TWO_COLORS, 'timeout': 0}],

    # TX
    'import_p12_ok': [
        {'id_led': LED_EXIT, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ENTRY, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ANTENNA, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000}],
    'import_p12_error': [
        {'id_led': LED_EXIT, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ENTRY, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ANTENNA, 'color': BLACK, 'behavior': FIXED, 'timeout': 1000}],
    'tx_auth_ok': [
        {'id_led': LED_ANTENNA, 'color': GREEN, 'behavior': FIXED, 'timeout': 1000}],
    'tx_auth_error': [
        {'id_led': LED_ANTENNA, 'color': RED, 'behavior': FIXED, 'timeout': 1000}],
    'tx_espera_listado_actas': [
        {'id_led': LED_ENTRY, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0},
        {'id_led': LED_ANTENNA, 'color': CYAN, 'behavior': SEESAW, 'timeout': 0}],
    'tx_acta_error': [
        {'id_led': LED_EXIT, 'color': RED, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ENTRY, 'color': RED, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ANTENNA, 'color': RED, 'behavior': FIXED, 'timeout': 1000}],
    'tx_acta_ok': [
        {'id_led': LED_EXIT, 'color': GREEN, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ENTRY, 'color': GREEN, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ANTENNA, 'color': GREEN, 'behavior': FIXED, 'timeout': 1000}],
    'tx_acta_repetida': [
        {'id_led': LED_EXIT, 'color': YELLOW, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ENTRY, 'color': YELLOW, 'behavior': FIXED, 'timeout': 1000},
        {'id_led': LED_ANTENNA, 'color': YELLOW, 'behavior': FIXED, 'timeout': 1000}],
    'tx_acta_espera_confirmacion': [
        {'id_led': LED_EXIT, 'color': BLACK, 'behavior': SEESAW, 'timeout': 0},
        {'id_led': LED_ENTRY, 'color': BLACK, 'behavior': SEESAW, 'timeout': 0},
        {'id_led': LED_ANTENNA, 'color': BLACK, 'behavior': SEESAW, 'timeout': 0}]
}
