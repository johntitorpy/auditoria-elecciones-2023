"""Helpers para el modulo Asistida."""
from datetime import datetime

from msa.modulos.asistida.constants import TIMEOUT_BEEP


def ultimo_beep(controlador):
    """
    Se verifica el tiempo transcurrido desde que se presionó la
    última tecla.
    En caso de que el tiempo sea mayor al establecido en la
    constante ``TIMEOUT_BEEP``, llama a la función "recordar" para
    que repita las opciones disponibles y confirme.

    Args:
        controlador (Controlador): Controlador del módulo de Asistida.

    Returns:
        bool: Devuelve siempre ``True``
    """
    if controlador.ultima_tecla is not None:
        time_diff = datetime.now() - controlador.ultima_tecla
        if time_diff.total_seconds() > TIMEOUT_BEEP:
            controlador.ultima_tecla = None
            controlador.asistente.recordar()
    return True
