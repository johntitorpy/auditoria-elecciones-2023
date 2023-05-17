"""
Modulo que maneja el ingreso de datos de los usuarios.

Maneja 3 pantallas distintas:
    * Introduccion de mesa y pin (usado en modulo Inicio)
    * Introduccion de datos personales (usado en Apertura y Escrutinio)
    * Pantalla de insercion de acta (usado en Apertura, pero soporta todos los
      tipos de acta)
"""
from cryptography.exceptions import InvalidTag
from gi.repository.GObject import timeout_add

from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.core.documentos.actas import Recuento
from msa.modulos import get_sesion
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.constants import (MODULO_MENU, MODULO_RECUENTO)
from msa.modulos.copias_certificado.controlador import Controlador
from msa.modulos.copias_certificado.rampa import RampaCopiasCertificado


from msa.settings import DEBUG


class Modulo(ModuloBase):

    """ Modulo de ingreso de datos.
        Este modulo funciona como submodulo de Inicio, Apertura y Recuento.
        Muestra las siguientes 3 "pantallas":
            * Ingreso de Mesa y PIN
            * Ingreso de Datos Personales
            * Ingreso de Actas y Certificados
    """
    def __init__(self, nombre):
        """Constructor."""
        self.sesion = get_sesion()
        self.nombre = nombre
        self.tipo_acta_a_copiar = None
        self.web_template = "copias_certificado"
        self.sesion.logger.info(self.nombre)

        # Pantalla de introduccion de mesa y pin del modulo Inicio
        self.rampa = RampaCopiasCertificado(self)
        self.controlador = Controlador(self)
        ModuloBase.__init__(self, nombre)
        
        self.rampa.set_led_action('espera_en_antena')
        self.config_files = [COMMON_SETTINGS, "copias_certificado"]
        self._load_config()
        self._start_audio()

    def document_ready(self):
        """Inicializamos cuando el browser tira el evento de document ready."""
        # Mandamos las constantes que el modulo necesita para operar.
        self.controlador.send_constants()
        # llamamos al maestro de ceremonias de la rampa para que evalúe como
        # proceder
        self.rampa.maestro()

    def set_pantalla(self, pantalla):
        """Setea la pantalla indicada."""
        self.controlador.set_screen(pantalla)

    def salir(self):
        self.salir_a_menu()

    def reiniciar_modulo(self):
        """Reinicia modulo."""
        self.controlador._inicializa_pantalla()

    def salir_a_menu(self):
        """ Sale del módulo de apertura, vuelve al comienzo con la maquina
            desconfigurada.
        """
        if hasattr(self, 'pantalla') and self.pantalla is not None:
            self.pantalla.destroy()
        if self.browser is not None:
            self.ventana.remove(self.browser)
        self.rampa.remover_consultar_lector()
        self.ret_code = MODULO_MENU
        self.quit()

    def cargar_recuento_copias(self, datos_tag):
        """Carga el modulo recuento en modo de copia de actas"""
        if self.tipo_acta_a_copiar == None:
            return
        recuento = None
        try:
            mesa = self.sesion.mesa
            try:
                recuento = Recuento.desde_tag(datos_tag.datos,
                                              serial=datos_tag.serial,
                                              aes_key=mesa.get_aes_key())

                #if recuento is None and Recuento.data_remaining:
                #    self.controlador.send_command('secuencia_correcta', {'partes': Recuento.parts_rem})
            except InvalidTag:
                self.logger.warning("Revisar código de control")
                if DEBUG:
                    self.show_dialogo("verificar_acta")
                else:
                    recuento = Recuento.desde_tag(datos_tag.datos)
            #except BadTagSecuence:
            #    self.logger.warning("La secuencia de actas fué ingresada en orden incorrecto. Borrando datos parciales")
            #    Recuento.clean_readed_data()
            #    self.controlador.send_command('error_secuencia')
        except Exception:
            self.show_dialogo("error_lectura", btn_aceptar="Aceptar")

        if recuento.mesa.parent!=mesa.parent:
            self.logger.exception("No se puede copiar actas de otro establecimiento")
            self.show_dialogo("copia_acta_otro_establecimiento", btn_aceptar="Aceptar")
            self.sesion.mesa.usar_cod_datos()
        else:
            if recuento is not None:
                recuento.reimpresion = {
                    "acta": self.tipo_acta_a_copiar
                }
                self.sesion.recuento = recuento
                self.ret_code = MODULO_RECUENTO
                self.quit()
            else:
                timeout_add(4000, self.hide_dialogo)

    def seleccionar_acta_a_copiar(self, tipo_acta):
        self.tipo_acta_a_copiar = tipo_acta
