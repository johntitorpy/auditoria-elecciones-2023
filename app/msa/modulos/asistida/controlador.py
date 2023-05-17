"""Controlador para el modulo Asistida."""
from datetime import datetime
from os.path import join

from gi.repository.GObject import timeout_add_seconds

from msa.constants import COD_LISTA_BLANCO
from msa.core.audio.settings import VOLUMEN_GENERAL
from msa.core.data.candidaturas import (Agrupacion, Candidatura, Categoria,
                                        Lista)
from msa.modulos.asistida.asistentes import (AsistenteAdhesion,
                                             AsistenteCandidatos,
                                             AsistenteCargoListas,
                                             AsistenteConfirmacion,
                                             AsistenteConsultaPopular,
                                             AsistenteListaCompleta,
                                             AsistenteModos, AsistentePartido,
                                             AsistentePartidosCat,
                                             AsistenteVerificacion,
                                             AsistenteCandidatoListas,
                                             AsistentePreferenciasCandidato,
                                             AsistenteCandidatosParaguay,
                                             AsistenteConsultaPopularParaguay,
                                             AsistenteConfirmacionParaguay,
                                             AsistenteVerificacionParaguay)
from msa.modulos.asistida.constants import PATH_TONOS, TIEMPO_ITER_TIMEOUT
from msa.modulos.asistida.helpers import ultimo_beep
from msa.modulos.constants import MODULO_ASISTIDA
from msa.modulos.sufragio.controlador import Controlador as ControllerVoto


class Controlador(ControllerVoto):

    """Controller para la interaccion con la interfaz de Asistida."""

    def __init__(self, *args, **kwargs):
        """Constructor del controlador."""
        ControllerVoto.__init__(self, *args, **kwargs)
        self.nombre = MODULO_ASISTIDA
        self.modulo._start_audio()
        if self.modulo._player is not None:
            self.modulo._player.set_volume(VOLUMEN_GENERAL)

        self.ultima_tecla = None

        timeout_add_seconds(TIEMPO_ITER_TIMEOUT, ultimo_beep, self)

    def audios_pantalla_modos(self, data):
        """
        Carga los audios de la pantalla de modos.

        Args:
            data (dict): Contiene los modos de votación, es decir
                si es por categorías o lista completa.
        """
        self.audios("pantalla_modos", data)

    def audios_cargar_candidatos(self, data):
        """
        Carga los audios de los candidatos.

        En base al diccionario recibido, se recuperan los datos de cada candidato
        para guardarlos en una lista. La misma se envían para ser reproducidos.

        Args:
            data (dict): Contiene información asociada a los candidatos.
        """
        data_dict = {"cod_categoria": data[0]}
        candidatos = []
        for elem in data[1]:
            candidato = Candidatura.one(id_umv=elem).to_dict()
            candidatos.append(candidato)

        data_dict["candidatos"] = candidatos
        self.audios("cargar_candidatos", data_dict)

    def audios_cargar_consulta(self, data):
        """
        Carga los audios de la consulta popular.

        Args:
            data (dict): Contiene el código de la consulta popular y la candidatura del mismo.
        """
        data_dict = {"cod_categoria": data[0]}
        candidatos = []
        for elem in data[1]:
            candidato = Candidatura.one(id_umv=elem).to_dict()
            candidatos.append(candidato)
        data_dict["candidatos"] = candidatos
        self.audios("cargar_consulta_popular", data_dict)

    def audios_cargar_listas(self, data):
        """
        Carga los audios de las listas.

        Args:
            data (dict): Contiene los identificadores de las listas.
        """
        listas = []

        for datum in data:
            if datum != COD_LISTA_BLANCO:
                lista = Lista.one(id_candidatura=datum).to_dict()
            else:
                lista = Candidatura.first(clase="Blanco").to_dict()
            listas.append(lista)

        self.audios("cargar_listas", listas)

    def audios_cargo_listas(self, data):
        """
        Carga los audios de las lista de los cargos.

        Args:
            data (dict): Contiene las candidaturas.
        """
        listas = []
        for datum in data:
            if datum:
                lista = Candidatura.one(id_umv=datum).to_dict()
                listas.append(lista)
            elif datum == 0:
                # casos especiales como "agrupaciones_municipales"
                listas.append({"codigo": "0", "texto_asistida": ""})
        self.audios("cargar_cargo_listas", listas)

    def audios_mostrar_confirmacion(self, data):
        """
        Carga los audios de la confirmacion.

        Args:
            data (dict): Contiene las categorías y los candidatos.
        """
        categorias = Categoria.many(sorted="posicion")
        cat_list = []
        for categoria in categorias:
            cat_dict = {}
            cat_dict['categoria'] = categoria.to_dict()
            if categoria.posee_preferencias:
                cands = self.modulo.seleccion.preferencias_elegidas(
                        categoria.codigo)
            else:
                cands = self.modulo.seleccion.candidato_categoria(
                        categoria.codigo)
            
            candidatos = [cand.to_dict() for cand in cands]

            cat_dict['candidatos'] = candidatos
            cat_list.append(cat_dict)
        self.audios("mostrar_confirmacion", cat_list)

    def audios_partidos_categoria(self, data):
        """
        Carga los audios de los partidos en la categoria.

        Args:
            data (dict): Contiene los códigos de las categorías.
        """
        partidos = []
        for datum in data[1]:
            agrupacion = Agrupacion.one(datum).to_dict()
            agrupacion["cod_categoria"] = data[0]
            partidos.append(agrupacion)
        self.audios("cargar_partidos_categoria", partidos)

    def audios_partidos_completa(self, data):
        """
        Carga los audios de los partidos en lista completa.

        """
        partidos = []
        for datum in data:
            partido = Agrupacion.one(datum).to_dict()
            partidos.append(partido)
        self.audios("cargar_partidos_completa", partidos)

    def audios_cargar_listas_candidatos(self, data):
        data_dict = {"cod_categoria": data[0]}
        candidatos = []
        for elem in data[1]:
            candidato = Candidatura.one(id_umv=elem).to_dict()
            candidatos.append(candidato)

        data_dict["candidatos"] = candidatos
        self.audios("cargar_listas_candidatos", data_dict)

    def audios_cargar_preferencias_candidato(self, data):
        id_umv = data[0]
        candidatos = [cand.to_dict() for cand in
                      Candidatura.preferencias(id_umv=id_umv)]
        data_dict = {
            "cod_categoria": candidatos[0]['cod_categoria'],
            "candidatos": candidatos
        }
        self.audios("cargar_preferencias_candidato", data_dict)

    def audios(self, command, data=None):
        """
        Llama al asistente de cada uno de las pantallas.
        Para esto se basa en el comando enviado por parámetros.

        Args:
            command (str): Indica que asistente deberá invocarse.
            data (dict): Información asociada a lo que se tiene que reproducir.
        """
        interceptar = self.mapeo_comandos_asistentes()
        if command in list(interceptar.keys()):
            clase, key = interceptar[command]
            # self.modulo.logger.info("Clase a usar para comando {} -> {}".format(command, clase))
            self.asistente = clase(self, data, key)
            self.cambiar_monitor()
            if self.asistente.es_interactivo:
                self.send_command("mostrar_teclado")
    
    def mapeo_comandos_asistentes(self):
        """
        Devuelve un diccionario con la el asistente que instancia cada comando
        """
        return {
            "pantalla_modos": [AsistenteModos, None],
            "cargar_listas": [AsistenteListaCompleta, None],
            "cargar_adhesiones": [AsistenteAdhesion, 0],
            "cargar_consulta_popular": [AsistenteConsultaPopular, "candidatos"],
            "cargar_candidatos": [AsistenteCandidatos, "candidatos"],
            "mostrar_confirmacion": [AsistenteConfirmacion, None],
            "cargar_partidos_completa": [AsistentePartido, None],
            "cargar_partidos_categoria": [AsistentePartidosCat, None],
            "cargar_cargo_listas": [AsistenteCargoListas, None],
            "cargar_listas_candidatos": [AsistenteCandidatoListas, "candidatos"],
            "cargar_preferencias_candidato": [
                AsistentePreferenciasCandidato, "candidatos"],
            "mostrar_verificacion": [AsistenteVerificacion, None]
        }

    def numeral(self, numero):
        """
        Callback cuando se apreta en numeral.
        Dicha tecla hace que se proceda a la pantalla de confirmación de la selección.

        Args:
            numero (int): El número (de n cifras) que se escribió antes del
              numeral.
        """
        if numero.isalnum():
            numero = str(int(numero))
        self.asistente.elegir(numero)

    def asterisco(self, data):
        """
        Callback cuando se apreta en asterisco. El mismo hace que se
        proceda a la cancelación de la opción.

        Args:
            numero (int): El número (de n cifras) que se escribió antes del
                asterisco.
        """
        self.asistente.cancelar()

    def change_screen_insercion_boleta(self, data):
        """Callback que se llama cuando se cambia a la pantalla de insercion."""
        self.sesion.locutor.shutup()

    def change_screen_mensaje_final(self):
        """
        Callback que se llama cuando se cambia a la pantalla de mensaje.
        Construye el mensaje que deberá reproducirse.
        """
        mensaje = [self.asistente._("fin_votacion"),
                   self.asistente._("puede_verificar")]
        self.asistente._decir(mensaje)

    def cambiar_monitor(self):
        """
        Cambia el texto del monitor al del asistente actual.
        Envía la orden de que el texto sea ``cambiar_indicador_asistida``
        """
        ControllerVoto.send_command(self, "cambiar_indicador_asistida",
                                    self.asistente.get_monitor())

    def imagen_consulta(self):
        """
        Pisamos el método imagen_consulta para poder reproducir el audio en vez de
        visualizarlo por la panatalla.
        """
        self.modulo.seleccion = self._datos_verificacion
        categorias = Categoria.many(sorted="posicion")
        cat_list = []
        for categoria in categorias:
            cat_dict = {}
            cat_dict['categoria'] = categoria.to_dict()

            if categoria.posee_preferencias:
                cands = self.modulo.seleccion.preferencias_elegidas(
                        categoria.codigo)
            else:
                cands = self.modulo.seleccion.candidato_categoria(
                        categoria.codigo)
            
            candidatos = [cand.to_dict() for cand in cands]
            cat_dict['candidatos'] = candidatos
            cat_list.append(cat_dict)
        self.modulo.seleccion = None
        asistentes = self.mapeo_comandos_asistentes()
        clase, key = asistentes["mostrar_verificacion"]
        self.asistente = clase(self, cat_list, repetir=False)
        self._datos_verificacion = None

    def get_constants(self):
        """
        Guarda en un diccionario, las constantes definidas en
        la configuración.

        Returns:
            dict: Contantes utilizadas a lo largo del módulo.6
        """
        constants_dict = ControllerVoto.get_constants(self)
        constants_dict['asistida'] = True
        constants_dict['titulo'] = _("titulo_votacion_asistida")
        constants_dict['subtitulo'] = _("coloque_el_acrilico")
        constants_dict['subtitulo_contraste'] = \
            _("coloque_el_acrilico_contraste")

        return constants_dict

    def emitir_tono(self, tecla):
        """
        Emite un tono según la tecla pulsada.
        """
        if tecla == "*":
            tecla = "s"
        elif tecla == "#":
            tecla = "p"
        tono = join(PATH_TONOS, "%s.wav" % tecla)
        self.sesion.locutor.shutup()
        self.modulo._player.play(tono)

        if tecla not in ("p", "s"):
            self.ultima_tecla = datetime.now()
        else:
            self.ultima_tecla = None

class ControladorParaguay(Controlador):

    def mapeo_comandos_asistentes(self):
        """
        Devuelve un diccionario con la el asistente que instancia cada comando
        """
        comandos = super(ControladorParaguay, self).mapeo_comandos_asistentes()
        comandos["cargar_candidatos"] = [AsistenteCandidatosParaguay, "candidatos"]
        comandos["cargar_consulta_popular"] = [AsistenteConsultaPopularParaguay, "candidatos"]
        comandos["mostrar_confirmacion"] = [AsistenteConfirmacionParaguay, None]
        comandos["mostrar_verificacion"] = [AsistenteVerificacionParaguay, None]
        return comandos

    @staticmethod
    def categoria_con_presidente_vice(datos):
        try:
            return datos['codigo'] != 'BLC' and datos['cargo_ejecutivo'] and len(datos['secundarios_datos_extra']) == 2
        except Exception as e:
            return False