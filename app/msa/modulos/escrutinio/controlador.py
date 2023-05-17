"""Controlador del modulo escrutinio."""
from base64 import encodestring
from io import BytesIO
from json import dumps
from os.path import join
from urllib.parse import quote

from msa.constants import COD_LISTA_BLANCO, COD_TOTAL_VOTOS_COMPUTADOS
from msa.core.constants import PATH_TEMPLATES_VARS
from msa.core.data.candidaturas import Agrupacion, Candidatura, Categoria
from msa.core.documentos.constants import (CIERRE_CERTIFICADO,
                                           CIERRE_COPIA_FIEL,
                                           CIERRE_ESCRUTINIO,
                                           CIERRE_PREFERENCIAS,
                                           CIERRE_RECUENTO,
                                           CIERRE_TRANSMISION)
from msa.core.imaging.constants import (CONFIG_BOLETA_CIERRE,
                                        CONFIG_BOLETA_ESCRUTINIO,
                                        CONFIG_BOLETA_CERTIFICADO,
                                        CONFIG_BOLETA_TRANSMISION)
from msa.core.imaging.reverso import ImagenReversoBoleta
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.constants import (E_CLASIFICACION,
                                   E_RECUENTO,
                                   MODULO_INICIO,
                                   MODULO_RECUENTO,MODULO_COPIAS_CERTIFICADO)
from msa.modulos.escrutinio.constants import (ACT_BOLETA_NUEVA,
                                              ACT_BOLETA_REPETIDA, ACT_ERROR,
                                              ACT_ESPECIALES, ACT_INICIAL,
                                              ACT_VERIFICAR_ACTA,
                                              MINIMO_BOLETAS_RECUENTO, TEXTOS,
                                              TARJETAS_CANDIDATO_NUMEROS_TEMPLATES,
                                              TEMPLATES_FLAVORS)


# Para type hints

from msa.core.documentos.boletas import Seleccion


class Actions(BaseActionController):

    def document_ready(self, data):
        self.controlador.send_constants()

    def cargar_cache(self, data):
        """Cachea los dos de candidaturas y los manda a la UI."""
        self.controlador.cargar_datos()

    def inicializar_interfaz(self, data):
        recuento = self.controlador.sesion.recuento
        reimpresion_data = hasattr(
            recuento, "reimpresion") and recuento.reimpresion
        if reimpresion_data:
            self.controlador.modulo.habilitar_copia_certificados(
                reimpresion_data["acta"])
        self.controlador.actualizar(ACT_INICIAL, reimpresion=reimpresion_data)

    def salir_a_reimpresion(self, data):
        self.controlador.salir_a_reimpresion()


class Controlador(ControladorBase):

    """Controller para la interfaz web de recuento."""

    def __init__(self, modulo):
        super(Controlador, self).__init__(modulo)
        self.set_actions(Actions(self))
        self.textos = TEXTOS
        self._actualization_functions = {
            ACT_INICIAL: self._get_actualization_data_inicial,
            ACT_BOLETA_NUEVA: self._get_actualization_data_boleta_nueva,
            ACT_BOLETA_REPETIDA: self._get_actualization_data_boleta_repetida,
            ACT_ESPECIALES: self._get_actualization_data_especiales,
            ACT_ERROR: self._get_actualization_data_boleta_error
        }

    def cargar_datos(self):
        """
        Genera un diccionario con los datos del Juego de Datos utilizado.
        Para ello, divide la información en categorías, candidaturas y
        agrupaciones.
        Luego, envía la orden de cargar dichos datos.

        Returns:
            dict: Diccionario con la división de categorías, agrupaciones y
                candidaturas que conforman el juego de datos.
        """
        datos = {}
        datos['categorias'] = self.dict_set_categorias()
        datos['candidaturas'] = self.dict_set_candidaturas()
        datos['agrupaciones'] = self.dict_set_agrupaciones()
        self.send_command("cargar_datos", datos)

    def dict_set_categorias(self):
        """Envia el diccionario con los datos de las categorías."""
        categorias = Categoria.all().to_dict()
        return categorias

    def dict_set_candidaturas(self):
        """Envia el diccionario con los datos de las candidaturas."""
        candidatos = Candidatura.all().to_dict()
        return candidatos

    def dict_set_agrupaciones(self):
        """Envia el diccionario con los datos de las agrupaciones."""
        candidatos = Agrupacion.all().to_dict()
        return candidatos

    def _datos_tabla(self):
        """
        Devuelve como un diccionario los resultados de la votación.

        Returns:
            dict: Contiene el resultado de la votación.
        """
        ret = {}
        resultados = self.sesion.recuento.get_resultados()

        for key, value in resultados.items():
            ret[key] = value
        return ret

    def _datos_tachas(self):
        return self.sesion.recuento.get_tachas()

    def _datos_preferencias_agrupadas_por_principal(self):
        return self.sesion.recuento.get_all_preferencias_agrupadas_por_principal()

    def actualizar(self, tipo_actualizacion, seleccion=None,
                   reimpresion=False):
        """
        Función encargada de actualizar estado de la máquina.
        Se construye el diccionario con información asociada y se envía el
        comando actualizar.

         .. DANGER::
            ``encodestring`` se encuentra en desuso.


        Args:
            tipo_actualizacion (str): Nuevo estado al cual se le solicita a la máquina.
            seleccion (dict): Selección de candidatos. Voto.
            reimpresion (bool): Determina si
        """
        if (self.modulo.estado == E_RECUENTO or reimpresion
                or tipo_actualizacion == ACT_ESPECIALES):

            self.modulo.beep(tipo_actualizacion)

            qr_reimpresion = None
            if reimpresion:
                mostrar_qr_en_reimpresion = self.modulo.config("mostrar_qr_en_reimpresion")
                qr_reimpresion = self.sesion.recuento.a_qr_b64_encoded(
                    self.sesion.recuento.grupo_cat) if mostrar_qr_en_reimpresion else None

            upd_data = {
                "boletas_procesadas": self.sesion.recuento.boletas_contadas(),
                "datos_tabla": None,
                "imagen": None,
                "listas_especiales": None,
                "reimpresion": bool(reimpresion),
                "reimpresion_acta": None if not reimpresion else reimpresion["acta"],
                "qr_reimpresion": qr_reimpresion,
                "tipo": tipo_actualizacion,
                "total_general": None,
                "grupo_cat": self.sesion.recuento.grupo_cat,
            }

            actualization_data = self._actualization_functions[tipo_actualizacion](seleccion=seleccion)

            upd_data.update(actualization_data)

            if tipo_actualizacion != ACT_ESPECIALES and reimpresion:
                upd_data.update(self._get_actualization_data_reimpresion())

            self.send_command("actualizar", upd_data)
    
    def _get_image_from_seleccion(self, seleccion: Seleccion) -> str:
        """_summary_

        Args:
            seleccion (Seleccion): La seleccion de la cual se quiere obtener la imagen

        Returns:
            str: Imagen encodeada en utf-8 con formato base64 para mostrar en el front
        """
        muestra_html = self.modulo.config("muestra_svg")
        mostrar = {"en_pantalla": True}
        if muestra_html:
            data = seleccion.tomar_datos(mostrar)
            return dumps(data, check_circular=False)
        else:
            imagen = seleccion.a_imagen(mostrar)
            buffer = BytesIO()
            imagen.save(buffer, format="PNG")
            img_data = encodestring(buffer.getvalue())
            imagen = "data:image/png;base64,%s" % img_data.decode()
            return quote(imagen.encode("utf-8"))

    def _get_datos_tabla(self):
        res = {}

        res['datos_tabla'] = self._datos_tabla()
        res['datos_tachas'] = self._datos_tachas()

        res['datos_preferencias'] = {}

        res['datos_preferencias'] = self._datos_preferencias_agrupadas_por_principal()
        return res
    
    def _get_datos_especiales(self):
        
        res = {}

        res["orden_especiales"] = self.sesion.recuento.mesa.listas_especiales
        res["listas_especiales"] = self.sesion.recuento.listas_especiales
        res["total_general"] = self.sesion.recuento.total_boletas()

        return res

    def _get_actualization_data_boleta_nueva(self, **kwargs) -> dict:
        
        seleccion = kwargs['seleccion']
        
        res = {}

        res['imagen'] = self._get_image_from_seleccion(seleccion)
        res['seleccion'] = self.get_datos_seleccion(seleccion)

        for categoria in Categoria.many(sorted="posicion"):
            if categoria.posee_preferencias:
                preferencias_sel = seleccion.preferencias_elegidas(categoria.codigo)
                if 'preferencia_elegida' not in res:
                    res['preferencia_elegida'] = {}

                if categoria.codigo not in res['preferencia_elegida']:
                    res['preferencia_elegida'][categoria.codigo] = []
                
                # La preferencia_elegida se usa para resaltar las preferencias de la
                # seleccion actual
                if len(preferencias_sel) > 0:
                    for preferencia in preferencias_sel:                                
                        res['preferencia_elegida'][categoria.codigo].append({
                            'id_umv': preferencia.id_umv
                        })
        
        res.update(self._get_datos_tabla())

        return res
    
    def _get_actualization_data_boleta_repetida(self, **kwargs) -> dict:

        seleccion = kwargs['seleccion']
        
        res = {}

        res['imagen'] = self._get_image_from_seleccion(seleccion)
        res['seleccion'] = None

        return res
    
    def _get_actualization_data_inicial(self, **kwargs) -> dict:
        
        res = {}

        res.update(self._get_datos_tabla())

        return res
    
    def _get_actualization_data_especiales(self, **kwargs):
        
        res = {}

        res.update(self._get_datos_tabla())
        res.update(self._get_datos_especiales())

        return res

    def _get_actualization_data_boleta_error(self, **kwargs):
        
        res = {}

        return res

    def _get_actualization_data_reimpresion(self, **kwargs):
        
        res = {}

        res.update(self._get_datos_especiales())

        return res

    def get_datos_seleccion(self, seleccion):
        """
        Devuelve los candidatos de una selección ordenados por categoría.

        Args:
            seleccion (dict): Seleción de candidatos. Voto.

        Returns:
            Array: Arreglo con la selección de los candidatos ordenados.
        """
        cand_seleccion = []
        for categoria in Categoria.many(sorted="posicion"):
            candidatos = seleccion.candidato_categoria(categoria.codigo)
            candidatos.sort(key=lambda c: c.nro_orden)
            if not categoria.posee_preferencias:
                cand_seleccion.append(candidatos[0].id_umv)
            else:
                cand_seleccion.append([c.id_umv for c in candidatos])

        return cand_seleccion

    def cargar_clasificacion_de_votos(self, data):
        """
        Contruye un diccionario con la cantidad de boletas procesadas,
        boletas totales y listas especiales.
        Luego, se solicita a la máquina que ejecute el comando
        ``pantalla_clasificacion_votos`` con la data que construyó.
        """
        self.modulo.estado = E_CLASIFICACION
        boletas_procesadas = self.sesion.recuento.boletas_contadas()
        total = self.sesion.recuento.total_boletas()
        listas_especiales = self.sesion.recuento.mesa.listas_especiales

        datos = {"boletas_procesadas": boletas_procesadas,
                 "boletas_totales": total,
                 "listas_especiales": listas_especiales}
        self.modulo.rampa.set_led_action('reset')
        self.send_command("pantalla_clasificacion_votos", datos)

    def guardar_listas_especiales(self, data):
        """
        Recibe por parámetro las listas especiales que deberan ser actualizadas.

        Args:
            data (dict): Contiene las listas especiales que deben ser contabilizadas.
        """
        for lista in self.sesion.recuento.mesa.listas_especiales:
            self.sesion.recuento.actualizar_lista_especial(lista,
                                                           data[lista])
        self.actualizar(ACT_ESPECIALES)

    def iniciar_secuencia_impresion(self, data=None):
        """
        Envía la orden de imprimir el recuento.
        """
        self.modulo.imprimir_documentos()

    def _get_imagen_reverso_acta(self, tipo):
        """
        Devuelve la imagen que pertenece al reverso del acta.

        Args:
            tipo (str): Indica el tipo de acta sobre el cual, se buscara la imagen

        Returns:
            ImagenReversoBoleta: Archivo svg que va al dorso de la boleta.
        """
        configs_svg = {
            CIERRE_RECUENTO: CONFIG_BOLETA_CIERRE,
            CIERRE_TRANSMISION: CONFIG_BOLETA_TRANSMISION,
            CIERRE_ESCRUTINIO: CONFIG_BOLETA_ESCRUTINIO,
            CIERRE_COPIA_FIEL: CONFIG_BOLETA_ESCRUTINIO,
            CIERRE_CERTIFICADO: CONFIG_BOLETA_ESCRUTINIO
        }
        return ImagenReversoBoleta(configs_svg[tipo]).render_svg()

    def pedir_acta(self, tipo):
        """
        Envía la orden para mostrar la pantalla en donde se solicita un acta.
        Para ello, también se pide la imagen que corresponde al tipo de acta.

        Args:
            tipo (str): Determina el tipo de acta.

        """
        imagen = self._get_imagen_reverso_acta(tipo)
        self.send_command("pantalla_pedir_acta",
                          {"tipo": tipo, "imagen": quote(imagen)})

    def set_pantalla_asistente_cierre(self):
        usar_qr = self.modulo.config("usar_qr")
        qr = self.sesion.recuento.a_qr_b64_encoded(
            self.sesion.recuento.grupo_cat) if usar_qr else None
        self.send_command("pantalla_asistente_cierre", qr)

    def set_pantalla_anterior_asistente(self):
        """
        Envía la orden para mostrar la pantalla anterior, con respecto
        a la actual.
        """
        self.send_command("show_slide")

    def habilitar_recuento(self, data):
        """
        Setea el estado de ``RECUENTO`` .
        """
        self.modulo.estado = E_RECUENTO

    def preguntar_salida(self):
        """
        Envía la orden de mostrar la pantalla de salida.
        """
        self.send_command("preguntar_salida")

    def aceptar_salida(self, data):
        """
        Envía la orden de salir del módulo de inicio.
        """
        self.modulo.salir()

    def mostrar_imprimiendo(self):
        """
        Envía la orden de mostrar el mensaje que indica
        que se esta imprimiendo.
        """
        self.send_command("mensaje_imprimiendo")

    def mostrar_pantalla_copias(self):
        """
        Envía la orden de mostrar la pantalla que indica
        que hay copias.
        """
        self.send_command("pantalla_copias",
                          self.sesion.recuento.reimpresion["acta"])

    def salir_a_reimpresion(self):
        self.modulo.sesion.recuento = None
        self.modulo.rampa.remover_boleta_expulsada()
        self.sesion.mesa.usar_cod_datos()
        self.modulo.salir_a_modulo(MODULO_COPIAS_CERTIFICADO)

    def apagar(self, data):
        """
        Envía la orden de apagado de la máquina.
        """
        self.modulo.apagar()

    def get_desc_especiales(self):
        desc_especiales = {}
        for lista in self.sesion.mesa.listas_especiales:
            file_name = "escrutinio/descripcion_votos_{}.txt".format(lista)
            path = join(PATH_TEMPLATES_VARS, file_name)
            with open(path, "r") as file_:
                desc_especiales[lista] = file_.read().strip()

        return desc_especiales

    def get_constants(self):
        """
        Genera un diccionario con constantes utilizadas por el módulo de
        escrutinio.

        Returns:
              dict: Diccionario con constantes.
        """
        textos_especiales = {lista: _("titulo_votos_{}".format(lista)) for
                             lista in self.sesion.mesa.listas_especiales}
        textos_especiales[COD_TOTAL_VOTOS_COMPUTADOS] = _("total_vco")
        desc_especiales = self.get_desc_especiales()
        PATH_EXTENSION_JS_MODULO = join("js", MODULO_RECUENTO, "extension")

        local_constants = {
            "cod_lista_blanco": COD_LISTA_BLANCO,
            "templates": self.get_templates(),
            "tarjetas_candidato_numeros_templates": TARJETAS_CANDIDATO_NUMEROS_TEMPLATES,
            "MINIMO_BOLETAS_RECUENTO": MINIMO_BOLETAS_RECUENTO,
            "titulos_especiales": textos_especiales,
            "tipo_act": {
                "ACT_INICIAL": ACT_INICIAL,
                "ACT_BOLETA_NUEVA": ACT_BOLETA_NUEVA,
                "ACT_BOLETA_REPETIDA": ACT_BOLETA_REPETIDA,
                "ACT_ERROR": ACT_ERROR,
                "ACT_ESPECIALES": ACT_ESPECIALES,
                "ACT_VERIFICAR_ACTA": ACT_VERIFICAR_ACTA,
            },
            "descripcion_especiales": desc_especiales,
            "TABLA_MUESTRA_ALIANZA": self.modulo.config("tabla_muestra_alianza"),
            "TABLA_MUESTRA_PARTIDO": self.modulo.config("tabla_muestra_partido"),
            "numero_mesa": self.sesion.recuento.mesa.numero,
            "USAR_NOMBRE_CORTO": self.modulo.config("usar_nombre_corto"),
            "USAR_COLOR": self.modulo.config("mostrar_color"),
            "limitar_candidatos": self.modulo.config("limitar_candidatos"),
            "USAR_NUMERO_LISTA": self.modulo.config("mostrar_numero_lista"),
            "totalizador": False,
            "muestra_svg": self.modulo.config("muestra_svg"),
            "templates_compiladas": self.modulo.config("templates_compiladas"),
            "PATH_EXTENSION_JS_MODULO": PATH_EXTENSION_JS_MODULO
        }
        constants_dict = self.base_constants_dict()
        constants_dict.update(local_constants)
        constants_dict["mostrar_ubicacion"] = False
        return constants_dict

    def get_templates_flavor(self, flavor=None):
        """Devuelve las templates a precachear."""
        template_names = TEMPLATES_FLAVORS['common']
        if flavor is not None:
            template_names += TEMPLATES_FLAVORS[flavor]
        return template_names

    def get_templates(self):
        """
        Devuelve el template para mostrar el recuento de los candidatos.
        Construye la ruta para poder obtenerlo.

        Returns:
            dict: Diccionario con la ruta del template.
        """
        flavor = self.modulo.config("flavor")
        templates = {}
        template_names = ("candidato_recuento", )

        if flavor is not None:
            template_names += TEMPLATES_FLAVORS[flavor]

        for template in template_names:
            file_name = "%s.html" % template
            template_file = join(flavor, file_name)
            templates[template] = template_file

        return templates

    def get_templates_modulo(self):
        """
        Determina los templates que serán usados.

        Returns:
            array.array: Arreglo con los nombres de los template utilizados.

        """
        templates = [
            "campo_extra", "candidato", "context/panel_acciones",
            "context/panel_asistente", "context/panel_blanco",
            "context/panel_clasificacion", "context/panel_copias",
            "context/panel_derecho", "context/panel_estado",
            "context/panel_finalizar", "context/tabla", "context/teclado",
            "copias", "imprimiendo", "loading", "mensaje_confirmar_apagar",
            "mensaje_fin_escrutinio", "mensaje_pocas_boletas", "mensaje_salir",
            "pantalla_boleta", "pantalla_boleta_error",
            "pantalla_boleta_repetida", "pantalla_clasificacion_votos",
            "pantalla_verificar_acta", "pantalla_clasificacion_votos",
            "pantalla_copias", "pantalla_inicial", "pedir_acta",
            "slides/certificados_extra", "slides/devolucion_sobre",
            "slides/devolucion_urna", "slides/firmar_acta",
            "slides/qr_fiscales", "tabla", "colores", "tabla-preferentes",
            "escrutinio_confirmacion_tarjeta", "cargo-con-preferentes"
        ]
        return templates


class ControladorParaguay(Controlador):

    def _get_datos_especiales(self):
        
        res = {}

        orden_especiales = [COD_TOTAL_VOTOS_COMPUTADOS]
        orden_especiales.extend(self.sesion.recuento.mesa.listas_especiales)
        
        listas_especiales = {COD_TOTAL_VOTOS_COMPUTADOS: self.sesion.recuento.boletas_contadas()}
        listas_especiales.update(self.sesion.recuento.listas_especiales)
        
        res["orden_especiales"] = orden_especiales
        res["listas_especiales"] = listas_especiales
        res["total_general"] = self.sesion.recuento.total_boletas()

        return res