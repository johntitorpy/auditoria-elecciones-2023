"""
Modulo que maneja el ingreso de datos de los usuarios.

Maneja 3 pantallas distintas:
    * Introduccion de mesa y pin (usado en modulo Inicio)
    * Introduccion de datos personales (usado en Apertura y Escrutinio)
    * Pantalla de insercion de acta (usado en Apertura, pero soporta todos los
      tipos de acta)
"""
from cryptography.exceptions import InvalidTag
from gi.repository.GObject import idle_add, timeout_add

from msa.core.config_manager import Config
from msa.core.config_manager.constants import COMMON_SETTINGS
from msa.core.documentos.actas import Apertura, Recuento
from msa.modulos import get_sesion
from msa.modulos.base.modulo import ModuloBase
from msa.modulos.constants import (
    E_CARGA,
    E_CONFIGURADA,
    E_INGRESO_ACTA,
    E_INGRESO_DATOS,
    E_INICIAL,
    E_MESAYPIN,
    E_ID_MESA_Y_PIN,
    E_SETUP,
    MODULO_APERTURA,
    MODULO_INICIO,
    MODULO_MENU,
    MODULO_RECUENTO,
    SUBMODULO_DATOS_APERTURA,
    SUBMODULO_DATOS_ESCRUTINIO,
    SUBMODULO_MESA_Y_PIN_INICIO, E_CONFIRMACION,
)
from msa.modulos.ingreso_datos.controlador import Controlador, ControladorParaguay
from msa.modulos.ingreso_datos.rampa import RampaApertura, RampaEscrutinio, RampaInicio
from msa.settings import DEBUG


class Modulo(ModuloBase):

    """Modulo de ingreso de datos.
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
        self.web_template = "ingreso_datos"
        self._start_audio()
        config = Config(["ingreso_datos"])
        self._ingreso_datos_con_id = config.val("ingreso_datos_con_id")

        # Pantalla de introduccion de mesa y pin del modulo Inicio
        if nombre == SUBMODULO_MESA_Y_PIN_INICIO:
            if self._ingreso_datos_con_id:
                self.controlador = ControladorParaguay(self, E_ID_MESA_Y_PIN, MODULO_INICIO)
            else:
                self.controlador = Controlador(self, E_MESAYPIN, MODULO_INICIO)
            ModuloBase.__init__(self, nombre)
            self.rampa = RampaInicio(self)
            self.rampa.set_led_action("espera_en_antena")

        # Pantallas de introduccion de boleta e Introduccion de Datos
        # Personales del podulo de apertura
        elif nombre == SUBMODULO_DATOS_APERTURA:
            # en _tmp_apertura se guarda la instancia temporal de apertura que
            # usamos para manejar el "volver atras" antes de imprimir la
            # apertura
            
            if self.sesion._tmp_apertura:
                self.apertura = self.sesion._tmp_apertura
                self.estado = E_CARGA
                if self._ingreso_datos_con_id:
                    estado_controlador = E_CONFIRMACION
                else:
                    estado_controlador = E_INGRESO_DATOS
            else:
                if self._ingreso_datos_con_id:
                    self.estado = E_CARGA
                    estado_controlador = E_CONFIRMACION
                else:
                    self.estado = E_INICIAL
                    estado_controlador = None

            _controlador = ControladorParaguay if self._ingreso_datos_con_id else Controlador
            self.controlador = _controlador(self, estado_controlador, MODULO_APERTURA)
            ModuloBase.__init__(self, nombre)
            self.rampa = RampaApertura(self)
        # Pantalla de introduccion de datos personales del escrutinio
        elif nombre == SUBMODULO_DATOS_ESCRUTINIO:
            if hasattr(self.sesion, "apertura"):
                self.apertura = self.sesion.apertura
            self.estado = E_SETUP
            estado_controlador = E_INGRESO_DATOS
            self.controlador = Controlador(self, estado_controlador, MODULO_RECUENTO)
            ModuloBase.__init__(self, nombre)
            self.rampa = RampaEscrutinio(self)

        self.config_files = [COMMON_SETTINGS, "ingreso_datos"]
        self._load_config()

    def _cargar_ui_inicio(self):
        """Carga la UI del modulo."""
        ModuloBase._cargar_ui_web(self)
        self._inicio()
        self.controlador.set_pantalla()
        self.ventana.show_all()

    def set_pantalla(self, pantalla):
        """Setea la pantalla indicada."""
        self.controlador.set_screen(pantalla)

    def _inicio(self):
        """Funcion llamada desde el controlador."""
        self.controlador.send_constants()

    def _abrir_mesa(self, mesa):
        """Abre la mesa."""
        if mesa is not None:
            self.rampa.set_led_action("reset")
            self._mesa = mesa
            # Le seteo el atributo abierta si la configuración de la mesa fue
            # con el acta de apertura
            self.sesion.mesa = mesa
            # establezco el estado del modulo como "configurada"
            self.estado = E_CONFIGURADA
            # si es una elección que usa apertura vamos al modulo, sino
            # directamente mostramos el menú
            if self.config("realizar_apertura"):
                self.ret_code = SUBMODULO_DATOS_APERTURA
            else:
                self.ret_code = MODULO_MENU
            # expulsamos la boleta y salimos
            self.rampa.expulsar_boleta()
            idle_add(self.quit)
        else:
            # si la mesa no es válida volvemos al estado inicial y mostramos
            # pin incorrecto
            self.estado = E_INICIAL
            self.ventana.remove(self.ventana.children()[0])
            self._cargar_ui_web()
            self.ventana.show_all()
            self._pantalla_principal()
            self.controlador.msg_mesaypin_incorrecto()

    def salir(self):
        self.salir_a_menu()

    def procesar_tag_apertura(self, tag):
        """Procesa el tag que se apoya en el lector."""
        if tag.vacio and not tag.read_only:
            if self.controlador.estado == E_INGRESO_ACTA:
                if self.rampa.tiene_papel:
                    self.apertura = None
                    self.sesion.apertura = None

                    con_datos = self.config("con_datos_personales")
                    if con_datos:
                        self.cargar_datos()
                    else:
                        self.crear_apertura()
                else:
                    self.controlador.set_mensaje(_("apoyo_acta"))

        elif not tag.es_apertura():
            self.controlador.set_mensaje(_("acta_contiene_informacion"))

            def _expulsar():
                self.controlador.set_mensaje(self.controlador.MSG_APERTURA)
                self.rampa.expulsar_boleta()

            timeout_add(2500, _expulsar)

    def mensaje_inicial(self):
        """Muestra el mensaje_inicial, borra la apertura de la sesion."""
        self.apertura = None
        self.sesion.apertura = None
        self.controlador.mensaje_inicial()

    def volver(self, apertura):
        """Vuelve a la pantalla de inicial"""
        self.cargar_datos(apertura)

    def cargar_datos(self, apertura=None):
        """Callback de salida del estado inicial, que indica que se obtuvo un
        tag de apertura.  Ahora se pasa al estado de carga de datos,
        solicita el ingreso de datos del Presidente de Mesa.
        """
        self.estado = E_CARGA
        self.controlador.estado = E_INGRESO_DATOS

        hora = None
        autoridades = None
        if apertura is not None:
            hora = apertura.hora
            autoridades = [(autoridad.a_dict()) for autoridad in apertura.autoridades]

        self.controlador.set_pantalla({"hora": hora, "autoridades": autoridades})

    def cargar_apertura(self, tag):
        """Carga los datos de la apertura en el menu cuando se apoya."""
        apertura = Apertura.desde_tag(tag.datos)
        estado = self.controlador.estado
        mesa = self.sesion.mesa
        if estado != E_INGRESO_DATOS or (
            estado == E_INGRESO_DATOS and mesa.numero == apertura.mesa.numero
        ):
            self.apertura = apertura
            self.controlador.set_pantalla({"mesa": apertura.mesa.numero})

    def reiniciar_modulo(self):
        """Reinicia modulo."""
        
        if self._ingreso_datos_con_id:
            self.estado = E_CARGA
            self.controlador.estado = E_CONFIRMACION
        else:
            self.estado = E_INICIAL
            self.controlador.estado = E_INGRESO_ACTA
        self.controlador._inicializa_pantalla()

    def crear_apertura(self, autoridades=None, hora=None):
        """
        Recibe un instancia de Presidente de Mesa y del suplente con los datos
        que cargo el usuario.
        """
        if autoridades is None:
            autoridades = []
        self.sesion._tmp_apertura = Apertura(self.sesion.mesa, autoridades, hora)

        self.salir_a_apertura()

    def salir_a_apertura(self):
        self.ret_code = MODULO_APERTURA
        self.quit()

    def configurar_desde_apertura(self, tag):
        """
        Configura la mesa con los datos que contiene el tag.
        """
        # traemos el objeto apertura desde los datos del tag
        apertura = Apertura.desde_tag(tag.datos)

        # si la apertura es válida y el número de la mesa que estamos abriendo
        # coincide con el número de la mesa de la apertura apoyada abrimos la
        # mesa en caso contrario mostramos un mensaje de error
        if apertura.mesa is not None:
            if apertura.mesa.numero == self.sesion.mesa.numero:
                self.rampa.expulsar_boleta()
                apertura.mesa = self.sesion.mesa
                self.sesion.apertura = apertura
                self.rampa.desregistrar_eventos()
                timeout_add(500, self.salir_a_menu)
            else:
                self.controlador.set_mensaje(_("acta_mesa_erronea"))
                self.rampa.expulsar_boleta()

    def salir_a_menu(self):
        """Sale del módulo de apertura, vuelve al comienzo con la maquina
        desconfigurada.
        """
        if hasattr(self, "pantalla") and self.pantalla is not None:
            self.pantalla.destroy()
        if self.browser is not None:
            self.ventana.remove(self.browser)
        self.rampa.remover_consultar_lector()
        self.ret_code = MODULO_MENU
        self.quit()

    def generar_recuento(self, autoridades=None, hora=None):
        """
        Recibe un instancia de Presidente de Mesa, con los datos que cargo el
        usuario.
        """
        self.sesion.recuento = Recuento(self.sesion.mesa, autoridades, hora)
        self.ret_code = MODULO_RECUENTO
        self.quit()

    def cargar_recuento_copias(self, datos_tag):
        """Carga el modulo recuento en modo de copia de actas"""
        recuento = None
        try:
            mesa = self.sesion.mesa
            try:
                recuento = Recuento.desde_tag(
                    datos_tag.datos, serial=datos_tag.serial, aes_key=mesa.get_aes_key()
                )
            except InvalidTag:
                self.logger.warning("Revisar código de control")
                if DEBUG:
                    self.show_dialogo("verificar_acta")
                else:
                    recuento = Recuento.desde_tag(datos_tag.datos)
        except Exception:
            self.logger.exception("Imposible cargar recuento")
            self.show_dialogo("error_lectura")
        if recuento:
            recuento.reimpresion = True
            self.sesion.recuento = recuento
            self.ret_code = MODULO_RECUENTO
            self.quit()
        else:
            timeout_add(4000, self.hide_dialogo)
