"""Registrador del modulo sufragio.

Se encarga de manejar el almacenamiento e impresion de las BUE.
"""
from datetime import datetime

from gi.repository.GObject import timeout_add, source_remove


class Registrador(object):

    """La clase que maneja el registro en la boleta.
    Por "registrar" entendemos imprimir + guardar el chip.
    """

    def __init__(self, callback, modulo, callback_error):
        """Constructor del registrador de boletas."""
        pass
