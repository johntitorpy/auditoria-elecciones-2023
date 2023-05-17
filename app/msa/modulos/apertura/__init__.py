# -*- coding: utf-8 -*-
from gi.repository.GObject import timeout_add

from msa.modulos.constants import MODULO_MENU
from msa.modulos.apertura.controlador import Controlador
from msa.modulos.apertura.rampa import Apertura
from msa.modulos.apertura.registrador import RegistradorApertura
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.constants import (E_INICIAL, MODULO_INICIO,
                                   SUBMODULO_DATOS_APERTURA)
from msa.modulos.decorators import requiere_mesa_abierta


class Modulo(ModuloBase):

    """ Modulo de Apertura. Clase padre :meth:`modulos.base.modulo.ModuloBase`

        Este módulo permite generar el acta de apertura de una mesa.
        El usuario debe ingresar el acta en la maquina, agregar y confirmar sus
        datos e imprimirla.

        .. DANGER::
            .. todo::
                el constructor de :meth:`ModuloBase <modulos.base.modulo.ModuloBase>` se llama luego de setear algunas variables cuando en realidad
                deberia ser la primera linea del constructor de esta clase. Esto genera dependencias encadenadas entre
                Modulo y ModuloBase

        Attributes:
            web_template (str): Nombre del template web que se va a cargar para este modulo.

            rampa (modulos.apertura.rampa.Apertura): Instancia de la rampa de apertura.

            controlador (modulos.apertura.controlador.Controlador): Instancia del controlador del modulo apertura.

            _mensaje (str): No se usa internamente en esta clase.

            ret_code (str):
                Modulo al que se debe retornar luego de ejecutar
                :meth:`ModuloBase.main <modulos.base.modulo.ModuloBase.main>`.
                Es un atributo que se usa en :meth:`ModuloBase <modulos.base.modulo.ModuloBase>`.

                .. todo:: Debe ser un atributo de :meth:`ModuloBase <modulos.base.modulo.ModuloBase>`

            estado (str):
                Se usa para establecer el estado actual del modulo. Inicia en :const:`modulos.constants.E_INICIAL`

            registrador (modulos.apertura.registrador.RegistradorApertura):
                Instancia del registrador de apertura que se usa para mandar a imprimir la apertura en
                :meth:`~Modulo.confirmar_apertura`.

    """

    @requiere_mesa_abierta
    def __init__(self, nombre):
        """
        Arguments:
            nombre (str): parametro que se pasa al constructor de la clase :meth:`modulos.base.modulo.ModuloBase`

        """
        self.web_template = "apertura"
        self.rampa = Apertura(self)
        self.controlador = Controlador(self)
        self._mensaje = None

        ModuloBase.__init__(self, nombre)
        self._start_audio()

        self.ret_code = MODULO_INICIO
        self.estado = E_INICIAL
        self.registrador = RegistradorApertura(self)

    def callback_salir(self):
        """
        Callback llamado por ``self.registrador`` para salir del modulo. Establece el acta de apertura definitiva, borra
        la temporal y vuelve a :const:`modulos.constants.MODULO_MENU`.
        """
        self.sesion.apertura = self.sesion._tmp_apertura
        del self.sesion._tmp_apertura
        self.salir_a_modulo(MODULO_MENU)

    def callback_proxima_acta(self):
        """Callback llamado por el registrador para registrar otra acta."""
        self.controlador.proxima_acta()

    def reimprimir(self):
        """Intenta imprimir nuevamente."""
        timeout_add(100, self.controlador.reimprimir)

    def confirmar_apertura(self):
        """Le pide a ``self.registrador`` que intente registrar el ``ActaApertura`` temporal almacenada en la sesion
        actual."""
        self.registrador.registrar(self.sesion._tmp_apertura)

    def salir(self):
        """ Sale del módulo de apertura y vuelve al comienzo con la maquina
            desconfigurada (:const:`modulos.constants.MODULO_INICIO`)
        """
        self.salir_a_modulo(MODULO_INICIO)

    def mensaje_inicial(self):
        """
        No hace nada
        """
        pass

    def volver_atras(self):
        """
        Vuelve al submodulo de ingreso de datos de apertura.
        """
        self.salir_a_modulo(SUBMODULO_DATOS_APERTURA)
