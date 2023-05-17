"""Contiene los decoradores del modulo base."""
from functools import wraps
from msa.core.hardware.settings import USAR_PRESENCIA

rampa_corriendo = False


def semaforo(func):
    """
    Hace que no se puedan ejecutar 2 acciones al mismo tiempo. El objetivo del uso de este decorator es evitar race
    conditions con la rampa.
    """
    def _inner(self, *args, **kwargs):
        global rampa_corriendo
        if not rampa_corriendo:
            rampa_corriendo = True
            func(self, *args, **kwargs)
            rampa_corriendo = False
    # Es necesario esta asignación para que los
    # docstrings de la función decorada pueda reflejarse
    # en la documentación con Sphinx.
    _inner.__doc__ = func.__doc__
    return _inner

def si_tiene_conexion(func):
    """
    Verifica que se tenga conexion con el servicio ARMVE.

    .. Error:: no se debe usar un decorator para remplazar un IF que pregunta por un atributo de la clase!!

    Args:
        func: la funcion a ejecutar

    """

    @wraps(func)
    def _inner(self, *args, **kwargs):
        if self.tiene_conexion:
            return func(self, *args, **kwargs)
    return _inner

def presencia_on_required(func):
    @wraps(func)
    def with_presencia(self, *args, **kwargs):
        if USAR_PRESENCIA:
            return func(self, *args, **kwargs)
    return with_presencia
