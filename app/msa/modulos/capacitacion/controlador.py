"""Controlador del modulo capacitacion."""

from msa.core.data import Ubicacion
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.capacitacion.constants import MOSTRAR_DEPARTAMENTOS, TEXTOS
from msa.modulos.constants import (E_EN_CONFIGURACION, E_SETUP,
                                   MODULO_ASISTIDA, MODULO_CAPACITACION)


class Controlador(ControladorBase):

    """Controller para la interfaz web de la capacitación."""

    def __init__(self, modulo):
        """Constructor de controlador de Capacitación."""
        super(Controlador, self).__init__(modulo)
        self.set_actions(BaseActionController(self))
        self.estado = E_SETUP
        self.mesa = None
        self.textos = TEXTOS
        self.nombre = MODULO_CAPACITACION

    def document_ready(self, data):
        """Callback que se llama cuando el browser tira el document.ready()."""
        self.modulo._ready()

    def _get_data_mesas(self):
        """
        Devuelve la data de los botones de cada ubicacion diferente.

        Returns:
            list: Lista de botones diferentes.
        """

        grupos = []

        # Si estamos agrupando por algun nivel en especial armamos grupos.
        # Ojo: si entra desde inicio solo levanta la config default
        clase_grupos = self.modulo.config("agrupar_ubicaciones_por")
        if clase_grupos is not None:
            ubicaciones_grupos = Ubicacion.many(clase=clase_grupos)
            for ubic in ubicaciones_grupos:
                codigo_hijos = ubic.codigo + "."
                grupo = ubic.to_dict()
                grupo["hijos"] = self.get_hijos_grupo(codigo_hijos)
                grupos.append(grupo)
        else:
            # sino armamos un solo grupo.
            grupo = {}
            grupo["hijos"] = self.get_hijos_grupo()
            grupos.append(grupo)

        return grupos

    def get_hijos_grupo(self, codigo_hijos=None):
        """
        Obtiene una lista de mesas a partir de un código de ubicación recibido (que puede ser None). Dicha lista
        tiene mesas de ubicaciones diferentes.

        Args:
            codigo_hijos (str): Código de ubicación base para obtener ubicaciones 'hijas' a dicho
                código.

        Returns:
            list: Lista de mesas de ubicaciones diferentes.

        """
        if codigo_hijos is None:
            codigo_hijos = ""
        ubics = Ubicacion.many(codigo__startswith=codigo_hijos, clase="Mesa")
        # Uso un set para tomar las N distintas configuraciones
        configuraciones = set()
        # En mesas_capacitacion guardo las mesas de ejemplo.
        mesas_capacitacion = []

        # Tomo una mesa testigo por cada lugar diferente
        for obj in ubics:
            if obj.cod_datos not in configuraciones:
                configuraciones.add(obj.cod_datos)
                mesa = obj.to_dict()
                mesa['municipio'] = obj.distrito
                mesas_capacitacion.append(mesa)

        return mesas_capacitacion

    def cargar_botones(self):
        """Carga los botones a mostrar en el menú. Invoca al comando del front
        llamado ``cargar_botones_ubicaciones`` enviándole los datos de las mesas  """
        datos_mesas = self._get_data_mesas()
        self.send_command("cargar_botones_ubicaciones", datos_mesas)

    def configurar_mesa(self, data):
        """Configura la mesa seleccionada. Dependiendo del módulo que sea, inicia la capacitación
        asistida o no."""
        modulo, ubicacion = data
        self.modulo._configurar_ubicacion_capacitacion(ubicacion)

        if modulo == MODULO_ASISTIDA:
            self.modulo._iniciar_capacitacion_asistida()
        else:
            self.modulo._iniciar_capacitacion()

    def activar_impresion(self, nro_mesa):
        """Activa la impresión de la mesa recibida por parámetro. Establece el estado al controlador como
        :const:`E_EN_CONFIGURACION <modulos.constants.E_EN_CONFIGURACION>`."""
        if self.estado == E_SETUP:
            mesa = Ubicacion.one(id_unico_mesa=nro_mesa)
            self.modulo._configurar_ubicacion_capacitacion(nro_mesa)
            self.mesa = mesa
            mesa.usar_cod_datos()
            self.estado = E_EN_CONFIGURACION
            self.send_command('mensaje_impresion_boleta')
        else:
            self.send_command('mensaje_boleta_registrando')

    def error_boleta_no_vacia(self):
        self.hide_dialogo()
        self.send_command("error_impresion_boleta")
        self.fin_boleta_demo_error()


    def fin_boleta_demo(self):
        """Establece el estado del controlador como
        :const:`E_SETUP <modulos.constants.E_SETUP>`."""
        self.estado = E_SETUP

    def fin_boleta_demo_error(self):
        """Establece el estado del controlador como
        :const:`E_SETUP <modulos.constants.E_SETUP>`.

        Luego expulsa la boleta."""
        self.estado = E_SETUP
        self.modulo.rampa.expulsar_boleta()

    def consulta(self, *args, **kwargs):
        """Actualmente no hace nada."""
        pass

    def cancelar_impresion(self, data):
        """Cancela la impresión utilizando el método
        :meth:`modulos.capacitacion.controlador.Controlador.fin_boleta_demo`"""
        self.fin_boleta_demo()

    def get_constants(self):
        """Trae las constantes necesarios para el módulo."""
        constants = self.base_constants_dict()
        constants["preimpresion_boleta"] = \
            self.modulo.config("preimpresion_boleta")
        constants["mostrar_departamentos"] = MOSTRAR_DEPARTAMENTOS
        constants["items_columna"] = \
            self.modulo.config("items_columna")
        constants["mostrar_boton_capacitacion"] = \
            self.modulo.config("mostrar_boton_capacitacion")
        constants["mostrar_boton_asistida"] = \
            self.modulo.config("mostrar_boton_asistida")

        return constants
    
    def encender_led_espera_boleta(self, data):
        self.modulo.encender_led_espera_boleta()
    
    def procesar_dialogo(self, data):
        super().procesar_dialogo(data)
        if not data:
            self.modulo.reset_leds()
