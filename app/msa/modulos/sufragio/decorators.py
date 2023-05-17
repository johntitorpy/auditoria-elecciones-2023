"""Decoradores del modulo sufragio."""
from msa.modulos.constants import E_VOTANDO


def solo_votando(func):
    """
    Decorador para que solo se puedan hacer ciertas acciones
    cuando se esta votanto.

    Para ello se evalúa el estado actual del módulo.
    """
    def _inner(self, *args, **kwargs):
        if self.modulo.estado == E_VOTANDO:
            return func(self, *args, **kwargs)
        else:
            self.modulo.rampa.maestro()
    # Es necesario esta asignación para que los
    # docstrings de la función decorada pueda reflejarse
    # en la documentación con Sphinx.
    _inner.__doc__ = func.__doc__
    return _inner
