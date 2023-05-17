import math

from msa.core.config_manager import Config
from msa.core.data.candidaturas import Categoria
from msa.core.data.helpers import get_config
from msa.core.imaging import Imagen
from msa.core.imaging.constants import DIMENSIONES_BOLETA, DEFAULTS_MOSTRAR_BOLETA

from msa.core.logging import get_logger
from msa.settings import MODO_DEMO

logger = get_logger("boletas")


class ImagenBoleta(Imagen):
    """Clase para la imagen de la boleta."""

    def __init__(self, seleccion, mostrar, test_data=None):
        super().__init__()
        self.seleccion = seleccion
        self.data = None
        self.test_data = test_data
        self._mostrar = DEFAULTS_MOSTRAR_BOLETA
        if mostrar is not None:
            self._mostrar.update(mostrar)

    def render_image(self):
        renderer = self.get_renderer()
        data = self.generate_data()
        image = renderer.fetch_result(data)
        return image

    def generate_data(self):
        """Genera la data para mandar al template de la boleta."""
        self.data = {
            'ancho': DIMENSIONES_BOLETA['ancho_boleta'],
            'alto': DIMENSIONES_BOLETA['alto_boleta']
        }

        titulo, subtitulo, ubicacion = self._get_titulos()
        self.data['titulo'] = titulo
        self.data['subtitulo'] = subtitulo
        self.data['ubicacion'] = ubicacion
        self.data['secciones'] = self._get_datos_candidatos()
        self.data['watermark'] = self._get_watermark()
        self.data['troquel'], self.data['sub_troquel'] = self._get_troquel()
        self.data["flavor"] = self.config("flavor", self.seleccion.mesa.ancestros[0])

        """ 
            Calculo el número de filas, columnas, 
            el multiplicador del tamaño de la fuente
            y el multiplicador del padding del contenido 
            de la tarjeta, según el número de cargos a mostrar
        """
        self.data['n_secciones'] = len(self.data['secciones'])
        if self.data['n_secciones'] <= 2:
            self.data['n_filas'] = 1
        elif 3 <= self.data['n_secciones'] <= 7:
            self.data['n_filas'] = 2
        else:
            self.data['n_filas'] = 3
        self.data['n_columnas'] = math.ceil((self.data['n_secciones'] + 1) / self.data['n_filas'])

        """ 
            La propiedad 'previsualizacion' sirve para indicarle 
            al template dónde se va a mostrar la boleta renderizada.
            Esto permite aplicar estilos particulares para cuando la boleta
            se muestre en la previsualización (pantalla de agradecimiento).  
        """
        self.data['previsualizacion'] = False

        if self.test_data is not None:
            self.data['verificar_overflow'] = True
            self.data['id_seleccion'] = self.test_data['id_seleccion']

        return self.data

    def _get_datos_candidatos(self):
        """Devuelve los datos de los candidatos de la seleccion"""
        filter = {
            "sorted": "posicion"
        }
        # mostrar_adheridas -> Boolean
        mostrar_adheridas = self.config("mostrar_adheridas_boleta", self.seleccion.mesa.cod_datos)

        if not mostrar_adheridas:
            filter["adhiere"] = None

        categorias = Categoria.many(**filter)
        # candidatos = self.seleccion.candidatos_elegidos()
        candidatos = []
        cand_bloques = 0
        # Junto candidatos y preferencias
        for categoria in categorias:
            if categoria.posee_preferencias:
                cand = self.seleccion.preferencias_elegidas(categoria.codigo)
            else:
                cand = self.seleccion.candidato_categoria(categoria.codigo)
            if cand is not None and len(cand) > 0:
                candidatos.append(cand)
                if cand[0].categoria.adhiere is None or mostrar_adheridas:
                    cand_bloques += 1
        secciones = []
        categorias_usadas = []
        idx_categorias = [categoria.codigo for categoria in categorias]

        # Recorro las selecciones, traigo los datos del candidato.
        for candidato in candidatos:
            if candidato[0].categoria.adhiere is None or mostrar_adheridas:
                datos = self._get_datos_candidato(candidato[0],
                                                  idx_categorias,
                                                  categorias_usadas)
                secciones.append(datos)

        return secciones

    def _get_watermark(self):
        """ Devuelveve los datos de la posicion del watermark. """
        watermarks = []
        if (self.config_vista("watermark") and
                not self.config_vista("en_pantalla")):
            medidas_watermark = DIMENSIONES_BOLETA['pos_watermark']
            for posicion in medidas_watermark:
                watermark = (posicion[0], posicion[1], _("watermark_text"), posicion[2])
                watermarks.append(watermark)
        else:
            watermarks = False

        return watermarks

    def _get_troquel(self):
        """Devuelve los datos de lo que se debe imprimir en el troquel."""
        if self.config("muestra_troquel_en_boleta") and not self.config_vista("en_pantalla"):
            pos_troquel = DIMENSIONES_BOLETA['pos_troquel']

            troquel = (pos_troquel[0], pos_troquel[1], _("texto_troquel_1"),
                       pos_troquel[2])
            sub_troquel = (pos_troquel[3], pos_troquel[4], _("texto_troquel_2"),
                           pos_troquel[5])

            return troquel, sub_troquel
        else:
            return False, False

    def _get_escudo(self):
        pass

    def _get_titulos(self):
        """Genera los datos de los titulos de la boleta para el template."""
        datos = get_config('datos_eleccion')
        titulo = datos['titulo']
        subtitulo = datos['subtitulo']

        mostrar_ubicacion = self.config("mostrar_ubicacion_boleta",
                                        self.seleccion.mesa.codigo)
        ubicacion = False
        if mostrar_ubicacion:
            ubicacion = self._generar_bloque_ubicacion()

        return titulo, subtitulo, ubicacion

    @staticmethod
    def _generar_bloque_presidente_vice(candidato, nuevas_lineas):
        nuevas_lineas.append((None, 'Pdte. : {}'.format(candidato.lista.datos_extra['presidente'])))
        nuevas_lineas.append((None, 'Vice Pdte. 1° : {}'.format(candidato.lista.datos_extra['vice_1'])))
        nuevas_lineas.append((None, 'Vice Pdte. 2° : {}'.format(candidato.lista.datos_extra['vice_2'])))
        return nuevas_lineas

    def _generar_bloque_ubicacion(self):
        ubicaciones = []
        ubicacion = self.seleccion.mesa
        ubicacion = ubicacion.parent
        clase_mapper = {
            "Pais" : "Elección",
            "Departamento": "Distrito",
            "Distrito": "Departamento",
            "Localidad": "Zona",
            "Establecimiento": "Local"
        }
        while ubicacion is not None:
            descripcion = ''
            if (MODO_DEMO and (ubicacion.clase == "Pais" or ubicacion.clase == "Distrito")) or not MODO_DEMO:
                descripcion = ubicacion.descripcion.strip()

            texto = "{}: {}".format(clase_mapper[ubicacion.clase], descripcion)

            ubicaciones.append(texto)
            ubicacion = ubicacion.parent

        ubicaciones = ubicaciones[::-1]
        _ubicaciones = " | ".join(ubicaciones)

        return _ubicaciones

    @staticmethod
    def _generar_nro_lista_bloque(seccion, categoria, candidato):

        num_lista = None
        if candidato.es_blanco:
            texto_lista = ""
        elif categoria.consulta_popular:
            texto_lista = candidato.lista.nombre.upper()
        else:
            num_lista = candidato.lista.numero.lstrip("0")
            texto_lista = " ".join((_("palabra_lista"), num_lista))

        seccion["numero_lista"] = {
            "texto": texto_lista,
            "numero": num_lista,
        }

    def _generar_lista_bloque(self, seccion, categoria, candidato):

        nombre_lista = ''
        if not (candidato.es_blanco or categoria.consulta_popular):
            mostrar_partido = self.config("mostrar_partido_en_boleta", self.seleccion.mesa.cod_datos)

            if mostrar_partido and candidato.partido is not None \
                    and candidato.partido.nombre != candidato.lista.nombre:
                nombre_lista = candidato.partido.nombre

            nombre_lista = candidato.lista.nombre

        seccion["muestra_lista_en_primer_cargo"] = self.config("mostrar_numero_lista_solo_primer_cargo")
        seccion["nombre_lista"] = nombre_lista

    def _generar_candidato_bloque(self, seccion, categoria, candidato):

        _candidatos = []
        if not candidato.es_blanco:
            origen = []
            if categoria.posee_tachas:
                origen = self.seleccion.tachas_elegidas()
            elif categoria.posee_preferencias:
                origen = self.seleccion.preferencias_elegidas(categoria.codigo)

            # Nombre del primer candidato
            nombre_candidato = []
            nombre = candidato.nombre
            if categoria.consulta_popular and len(candidato.secundarios):
                nombre = " ".join(candidato.secundarios)

            # Cambia las comillas dobles a simples en la generación de la imagen de
            # la boleta para ser coherente con Zaguan que siempre reemplaza las
            # comillas simples por dobles al enviar los datos a javascript.
            nombre = nombre.replace('"', "'")

            _config = Config(["sufragio"])
            cargos_con_vicepresidente = _config.val("cargos_con_vicepresidente")
            cargos_con_vicepresidente_mujeres = _config.val("cargos_con_vicepresidente_mujeres")
            cargos_con_vice1_y_vice2 = _config.val("cargos_con_vice1_y_vice2")

            if candidato.cod_categoria in cargos_con_vicepresidente and not candidato.es_blanco:
                vices = candidato.candidatos_secundarios

                if candidato.cod_categoria in cargos_con_vicepresidente_mujeres:
                    nombre_candidato = [('Pdta.: {}'.format(nombre.replace('"', "'")))]
                else:
                    nombre_candidato = [('Pdte.: {}'.format(nombre.replace('"', "'")))]

                if candidato.cod_categoria in cargos_con_vice1_y_vice2:
                    for count, vices in enumerate(vices, start=1):
                        nombre_candidato.append('Vice {}° : {}'.format(count, vices.nombre.replace('"', "'")))
                else:
                    for count, vices in enumerate(vices, start=1):
                        nombre_candidato.append('Vice.: {}'.format(vices.nombre.replace('"', "'")))

            else:
                nombre_candidato.append(nombre)

            seleccionado = candidato in origen
            _candidatos = {
                "texto": nombre_candidato,
                "seleccionado": seleccionado,
                "nro_orden": candidato.nro_orden,
                "titulo": False,
            }
        else:
            _candidatos = {
                "texto": [candidato.nombre],
                "titulo": False,
            }

        # Agrega leyenda para el candidato principal (e.g. "Titular:")
        if self.config("mostrar_titulo_candidato_principal"):
            _candidatos["titulo"] = _("titulo_candidato_principal")

        seccion["nombre_candidato"] = _candidatos

    @staticmethod
    def _generar_secundarios_bloque(seccion, categoria, candidato):
        secundarios = candidato.secundarios
        candidatos_secundarios = []
        if len(secundarios) and not categoria.consulta_popular:
            candidatos_secundarios = [cand for cand in secundarios]

            seccion['secundarios'] = candidatos_secundarios
        else:
            seccion['secundarios'] = False

    def _generar_lista_secundarios_bloque(self, seccion, categoria, candidato):
        origen = []
        if categoria.posee_tachas:
            origen = self.seleccion.tachas_elegidas()
        elif categoria.posee_preferencias:
            origen = self.seleccion.preferencias_elegidas(categoria.codigo)

        cand_selec = []
        secundarios = []
        if len(origen):
            cand_selec = [c.id_umv for c in origen]
            secundarios = [_cand for _cand in candidato.candidatos_secundarios
                           if _cand.id_umv in cand_selec]
        else:
            secundarios = candidato.candidatos_secundarios

        # nombre del resto de los candidatos (si hay)
        if len(secundarios) and not categoria.consulta_popular:
            candidatos_secundarios = []
            for _candidato in secundarios:
                lineas_texto = []

                if not candidato.es_blanco and candidato.cod_categoria == 'PVC':
                    nuevas_lineas_texto = []
                    nuevas_lineas_texto = self._generar_bloque_presidente_vice(candidato, nuevas_lineas_texto)
                    nuevas_lineas_texto.append(
                        (None, 'Opción {} {}'.format(_candidato.nro_orden, _candidato.nombre))
                    )
                    _candidato.nro_orden = None
                    lineas_texto = nuevas_lineas_texto

                else:
                    lineas_texto.append(_candidato.nombre)

                seleccionado = _candidato.id_umv in cand_selec
                candidatos_secundarios.append({
                    "texto": lineas_texto,
                    "seleccionado": seleccionado,
                    "nro_orden": _candidato.nro_orden,
                })
            seccion['nombre_candidato'] = candidatos_secundarios

    def _generar_suplentes_bloque(self, seccion, categoria, candidato):
        # nombre del resto de los candidatos (si hay)
        suplentes = candidato.suplentes
        if suplentes:
            mostrar_suplentes = self.config("mostrar_suplentes_en_boleta", self.seleccion.mesa.cod_datos)
            candidatos_suplentes = []
            if mostrar_suplentes and len(suplentes) and not categoria.consulta_popular:
                candidatos_suplentes = [cand for cand in suplentes]

            seccion['suplentes'] = candidatos_suplentes
        else:
            seccion['suplentes'] = False

    def _generar_adherida_bloque(self, seccion, categoria):
        # si no quiero mostrar las categorias adheridas como paneles separados
        # seguramente quiera mostrar la seleccion dentro del bloque del padre
        mostrar_adheridas = self.config("mostrar_adheridas_boleta",
                                        self.seleccion.mesa.cod_datos)
        if not mostrar_adheridas:
            hijas = Categoria.many(adhiere=categoria.codigo)
            lineas_texto = []
            for hija in hijas:
                cands_hijos = self.seleccion.candidato_categoria(hija.codigo)
                if cands_hijos is not None:
                    candidatos = [cands_hijos[0].nombre]
                    candidatos += cands_hijos[0].secundarios
                    cand_hijo = "{}: {}".format(hija.nombre,
                                                "; ".join(candidatos))
                    lineas_texto.append(cand_hijo)
            seccion['adherentes'] = lineas_texto

    @staticmethod
    def _generar_template(posee_preferencias, es_blanco, muestra_secundarios, muestra_suplentes):

        if es_blanco:
            return "boleta_tarjeta_voto_blanco"
        elif posee_preferencias:
            return "boleta_tarjeta_con_preferencias"
        elif muestra_secundarios or muestra_suplentes:
            if muestra_secundarios and muestra_suplentes:
                return "boleta_tarjeta_con_secundarios_y_suplentes"
            elif muestra_secundarios:
                return "boleta_tarjeta_con_secundarios"
            else:
                return "boleta_tarjeta_con_suplentes"
        else:
            return "boleta_tarjeta_sin_preferencias"

    def _get_datos_candidato(self, candidato, idx_categorias, categorias_usadas):

        categoria = candidato.categoria

        index = idx_categorias.index(categoria.codigo)
        if categoria in categorias_usadas:
            index += categorias_usadas.count(categoria)
        categorias_usadas.append(categoria)

        # Voto en blanco
        seccion = {
            "es_blanco": candidato.es_blanco,
            "titulo": categoria.nombre.upper(),
            "usa_preferencia": False,
            "numero_lista": False,
        }

        # Esto resuelve si hay que habilitar preferencias
        if categoria.posee_preferencias and not candidato.es_blanco:
            seccion["usa_preferencia"] = True
            # Genero una lista de candidatos secundarios
            self._generar_lista_secundarios_bloque(seccion, categoria, candidato)

        # Genera la descripción del candidato
        self._generar_candidato_bloque(seccion, categoria, candidato)

        # genero la descripcion de la agrupación
        self._generar_lista_bloque(seccion, categoria, candidato)

        # genero el numero de lista si es necesario
        if self.config("mostrar_numero_lista_en_boleta"):
            self._generar_nro_lista_bloque(seccion, categoria, candidato)

        # genero los candidatos secundarios
        muestra_secundarios = False
        if self.config("mostrar_secundarios_en_boleta"):
            muestra_secundarios = True
            self._generar_secundarios_bloque(seccion, categoria, candidato)

        # genero los candidatos suplentes
        muestra_suplentes = False
        if self.config("mostrar_suplentes_en_boleta"):
            muestra_suplentes = True
            self._generar_suplentes_bloque(seccion, categoria, candidato)

        # genero los datos de la categoría adherida a este bloque
        if self.config("mostrar_adheridas_boleta"):
            self._generar_adherida_bloque(seccion, categoria)

        seccion["template"] = self._generar_template(categoria.posee_preferencias,
                                                     candidato.es_blanco,
                                                     muestra_secundarios,
                                                     muestra_suplentes)

        return seccion
