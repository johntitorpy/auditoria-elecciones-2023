import textwrap

from copy import copy, deepcopy
from os.path import join

from msa.constants import COD_TOTAL
from msa.core.constants import PATH_IMAGENES_VARS
from msa.core.data.candidaturas import Agrupacion, Candidatura, Categoria
from msa.core.documentos.constants import (CIERRE_PREFERENCIAS)
from msa.core.imaging import Imagen, jinja_env
from msa.core.imaging.constants import (COLORES, DEFAULTS_MOSTRAR_ACTA,
                                        MEDIDAS_ACTA)
from msa.settings import MODO_DEMO
from abc import abstractmethod

from msa.core.imaging.actas.decorators import en_pantalla

from msa.core.data import Ubicacion

class ImagenActa(Imagen):
    
    def __init__(self):
        """Constructor.

        Argumentos:
            
        """        
        self.render_template()

    def _generate_data(self):

        self._data = {
            "colores": COLORES,
            "medidas": self._get_medidas(),
            "encabezado": self._get_encabezado(),
            "i18n": self._get_i18n(),
            "qr": self._get_qr(),
            "mesa": self._get_mesa(),
            "escudo": self._get_escudo(),
            "verificador": self._get_verificador(),
            "watermark": self._get_watermark(),
            "en_pantalla": self.config_vista("en_pantalla"),
            "leyenda": self._get_leyenda(),
            "pie": self._get_pie(),
            "horas": self._get_horas(),
            "minutos": self._get_minutos(),
            "presidente": self._get_presidente(),
            "suplentes": self._get_suplentes(),
            "cantidad_suplentes": self._get_cantidad_suplentes(),

        }
        self._data["texto_acta"] = self._get_texto()
        self._data["posiciones"] = self._get_posiciones()
        
        from pprint import pformat
        print(pformat(self.data), flush=True)
    
    def _get_mesa(self) -> Ubicacion:
        """ Retorna la mesa relacionada al acta.

        Returns:
            Ubicacion: Instancia de ubicacion de tipo mesa.
        """
        ...

    def _get_medidas(self) -> 'dict[str, int]':
        """Devuelve las medidas del acta."""

        medidas = {
            "width": self._get_width(),
            "height": self._get_height(),
        }
        return medidas

    @abstractmethod
    def _get_width(self) -> int:
        """ Devuelve el ancho del acta

        Returns:
            int: Ancho del acta
        """
        ...

    @abstractmethod
    def _get_height(self) -> int:
        """ Devuelve el alto del acta

        Returns:
            int: Alto del acta
        """
        ...
    
    @abstractmethod
    def _get_posiciones(self, data) -> 'dict[str, int]':
        """Averigua la ubicacion de cada uno de los elementos del acta."""
        ...

    def _get_encabezado(self):
        """Devuelve los datos del encabezado"""
        
        _, wrap = MEDIDAS_ACTA['titulo']
        datos = {
            "nombre_acta": textwrap.wrap(self._get_titulo(), wrap),
            "texto": self._get_texto_encabezado()
        }

        return datos
    
    @abstractmethod
    def _get_titulo(self) -> str:
        """ Devuelve el título del acta

        Returns:
            str: titulo del acta
        """
        ...

    def _get_i18n(self):
        textos = {
            "mesa": _("mesa"),
            "firmas_autoridades": _("firmas_autoridades"),
            "firmas_fiscales": _("firmas_fiscales"),
            "firmas_fiscales_detalle": _("firmas_fiscales_detalle"),
            "agrupaciones": _("agrupaciones"),
            "titulo_especiales": _("titulo_especiales"),
            "cantidad": _("cantidad"),
        }

        return textos

    @en_pantalla
    def _get_qr(self, width):
        """Devuelve los datos del QR para el template."""
        ...

    def _get_escudo(self):
        """Devuelve los datos del escudo para el template."""
        logo = self._get_img_b64(join(PATH_IMAGENES_VARS, 'logo_boleta.png'))
        pos_x, pos_y = MEDIDAS_ACTA["escudo"]
        escudo = (pos_x, pos_y, logo)
        return escudo

    def _get_verificador(self):
        """Devuelve los datos del verificador para el template."""
        # muestro imagen verificador y corro margen superior hacia abajo
        if (not self.config_vista("en_pantalla")
                and self.config_vista("verificador")):
            verif_x, verif_y = MEDIDAS_ACTA["verificador"]
            img_verif = join(PATH_IMAGENES_VARS, 'verificador_alta.png')
            img_verif = self._get_img_b64(img_verif)

            return (verif_x, verif_y, img_verif)

    def _get_texto_encabezado(self):
        """Devuelve los datos de los titulos para el template."""
        lineas = []

        if not self.config_vista("en_pantalla"):
            # Esto sería un for si no cambiara tanto de eleccion a eleccion
            # probamos varias cosas con los años, esta es la solucion mas
            # customisable
            lineas = [
                _("encabezado_acta_1"),
                _("encabezado_acta_2"),
                _("encabezado_acta_3"),
                _("encabezado_acta_4")
            ]

        return lineas

    def _get_texto(self):
        """Devuelve los datos del texto del acta para el template."""
        texto = None
        if self.config_vista('texto'):
            # traigo los templates
            uri_tmpl_suplentes = "actas/textos/suplentes.tmpl"
            uri_tmpl_presidente = "actas/textos/presidente.tmpl"
            tmpl_suplentes = jinja_env.get_template(uri_tmpl_suplentes)
            tmpl_presidente = jinja_env.get_template(uri_tmpl_presidente)
            template = jinja_env.get_template(self.template_texto)
            # los renderizo y los meto en data
            self.data['texto_suplentes'] = tmpl_suplentes.render(**self.data)
            self.data['texto_presidente'] = tmpl_presidente.render(**self.data)
            # y le paso todo al template del texto para armar el texto del acta
            self.texto = template.render(**self.data)

            posicion, wrap = MEDIDAS_ACTA['texto']
            dy = posicion - MEDIDAS_ACTA['offset_top']
            texto = (dy, textwrap.wrap(self.texto, wrap))
        return texto

    def _get_watermark(self):
        """Devuelve el watermark de las actas."""
        watermarks = []
        if MODO_DEMO and not self.config_vista("en_pantalla"):
            # solo muestro la marca de agua si imprimo (con verificador)
            for posicion in MEDIDAS_ACTA['pos_watermark']:
                watermark = (posicion[0], posicion[1], _("watermark_text"),
                             posicion[2])
                watermarks.append(watermark)
        return watermarks

    def _get_datos_especiales(self):
        """Devuelve los valores para la tabla de listas especiales."""
        valores_especiales = []

        for lista_esp in self.recuento.mesa.listas_especiales:
            fila = (lista_esp, _("titulo_votos_%s" % lista_esp),
                    self.recuento.listas_especiales[lista_esp])
            valores_especiales.append(fila)

        # Armamos el total general
        general = self.recuento.boletas_contadas()
        general += sum(self.recuento.listas_especiales.values())
        valores_especiales.append((COD_TOTAL, _("total_general"), general))

        len_general = len(str(general))
        if len_general < 3:
            len_general = 3

        return valores_especiales, len_general
    
    def _get_datos_especiales_con_preferencias(self):
        """ Devuelve los valores para la tabla de listas especiales en el caso
            particular de impresión de tabla de preferencias."""

        categoria = Categoria.one(codigo=self._cargo_preferencias)
        
        valores_especiales = []

        # los votos blancos pasan a la tablita de votos especiales
        fila_blanca = self._get_datos_fila_blanca([categoria])
        
        valores_especiales.append(fila_blanca)

        for lista_esp in self.recuento.mesa.listas_especiales:
            fila = (lista_esp, _("titulo_votos_%s" % lista_esp),
                    self.recuento.listas_especiales[lista_esp])
            valores_especiales.append(fila)

        # Armamos el total general
        general = self.recuento.boletas_contadas()
        general += sum(self.recuento.listas_especiales.values())
        valores_especiales.append((COD_TOTAL, _("total_general"), general))

        len_general = len(str(general))
        if len_general < 3:
            len_general = 3

        return valores_especiales, len_general

    def _get_datos_tabla(self, categorias, agrupaciones):
        """Devuelve los datos de la tabla principal del acta.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
            agrupaciones -- las agrupaciones que participan en esta Ubicacion.
        """
        filas = []
        max_char = 3
        partido_omitido = False
        clases_a_mostrar = self.config("clases_a_mostrar",
                                       self.data["cod_datos"])
        colapsar_partido = self.config("colapsar_partido",
                                       self.data["cod_datos"])
        # Recorro todas las agrupaciones (Alianza, Partido, Lista)
        # viendo cual segun la forma de la eleccion y las configuraciones debo
        # mostrar
        for agrupacion in agrupaciones:
            # si esta la eleccion configurada para mostrar esa clase de
            # agrupacion
            clase = agrupacion.clase
            if clase in clases_a_mostrar:
                # colapso el partido si tiene una sola lista y esta habilitado
                if colapsar_partido and clase == "Partido":
                    partido_omitido = len(agrupacion.listas) == 1
                # Traigo los datos de la fila en caso de que tenga que
                # mostrarla
                if not partido_omitido or (partido_omitido and
                                           clase != "Partido"):
                    fila, chars_lista = self._get_datos_fila(categorias,
                                                             agrupacion,
                                                             partido_omitido)
                    # Las listas solo aparecen si tienen candidatos en
                    # categorias que queremos mostrar en este acta.
                    if (clase != "Lista" or not
                            all([elem == "-" for elem in fila[3:]])):
                        if chars_lista > max_char:
                            max_char = chars_lista

                        # no mostramos alianazas vacías
                        try:
                            if (clase == "Alianza" and
                                    filas[-1][3] == "Alianza"):
                                filas.pop(-1)
                        except IndexError:
                            pass

                        filas.append(fila)

        # Vemos si tenemos votos en blanco para agregar
        fila_blanca = self._get_datos_fila_blanca(categorias)
        if fila_blanca is not None:
            filas.append(fila_blanca)

        return filas, max_char

    def _get_datos_fila_blanca(self, categorias):
        """Devuelve los datos de la fila de votos en blanco.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
        """
        mostrar_numero = self.config("numero_lista_en_tabla",
                                     self.data["cod_datos"])
        numero = " " if mostrar_numero else ""
        # Manejo de la fila que tiene los votos en blanco
        fila = [numero, _("votos_en_blanco"), 0]
        # cantidad_blancos no es un booleano porque a veces en algunas
        # elecciones esta bueno saber cuantas candidaturas en blanco hay
        cantidad_blancos = 0
        # Recorro todas las categorias buscando las candidaturas blancas en
        # caso de que las haya
        for categoria in categorias:
            candidato = Candidatura.get_blanco(categoria.codigo)
            # el contenido del cuadro va a ser "-" a menos que haya algun
            # candidato blanco en esta categoria para esta Ubicacion
            resultado = "-"
            if candidato is not None:
                resultado = self.recuento.get_resultados(candidato.id_umv)
                # muestro la cantidad de blancos
                cantidad_blancos += 1
            fila.append(resultado)
        # si tengo candidatos blancos tenemos que mostar la fila de blancos.
        if not cantidad_blancos:
            fila = None

        return fila

    def _get_datos_fila(self, categorias, agrupacion, partido_omitido):
        """Devuelve los datos de la tabla principal del acta.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
            agrupacion -- la agrupacion de la que estamos mostrando la tabla
        """
        # primero vamos a averiguar la indentacion que queremos ponerle a esta
        # fila en la tabla.
        clases_a_mostrar = self.config("clases_a_mostrar",
                                       self.data["cod_datos"])
        mostrar_numero = self.config("numero_lista_en_tabla",
                                     self.data["cod_datos"])
        indentacion = clases_a_mostrar.index(agrupacion.clase)
        # si el partido no esta omitido vamos a ponerle profundidad.
        if not partido_omitido:
            nombre = " " * indentacion
            nombre += agrupacion.nombre
        # sino el nombre pasa de largo y queda el que está.
        else:
            nombre = agrupacion.partido.nombre
        # establecemos el numero de la lista. En alguna eleccion esto puede ser
        # mas complejo que traer el numero, puede ser la concatenacion de
        # varios numeros diferentes.
        if mostrar_numero and hasattr(agrupacion, "numero") and agrupacion.numero:
            numero = str(agrupacion.numero)
        else:
            numero = ""

        # armamos la base de la fila.
        fila = [numero, nombre, indentacion]

        # Recorremos todas las categorias que queremos mostrar en este acta
        # buscando cuantos votos tiene cada candidato.
        for categoria in categorias:
            candidato = Candidatura.one(cod_lista=agrupacion.codigo,
                                        cod_categoria=categoria.codigo)
            # Si el candidato existe vamos a buscar cuantos votos tiene y sino
            # devolvemos "-" que se transforma en una cruz en el acta
            if candidato is not None:
                votos = self.recuento.get_resultados(candidato.id_umv)
            else:
                votos = "-"
            fila.append(votos)

        return fila, len(numero)

    def _get_categorias(self):
        # Ordenamos siempre por la posicion de la Categoria.
        filter = {
            "sorted": "posicion",
        }

        # Quizas queremos omitir las categorias adheridas, como en algunas
        # elecciones en las que el vicegobernador es un cargo que adhiere al de
        # gobernador.
        mostrar_adheridas = self.config("mostrar_adheridas_acta",
                                        self.data["cod_datos"])
        if not mostrar_adheridas:
            filter["adhiere"] = None

        # En caso de querer generar la tabla con un solo grupo de categorias
        if self.grupo_cat is not None:
            filter["id_grupo"] = self.grupo_cat

        # Traemos todas las categorias con el filtro que acabamos de armar
        categorias = Categoria.many(**filter)

        return categorias

    def _get_tabla_votos(self):
        """Construye la tabla del recuento y devuelve los datos."""

        categorias = self._get_categorias()
        # traigo los datos de las listas especiales
        especiales, caracteres_categoria = self._get_datos_especiales()
        dx = MEDIDAS_ACTA['margen_derecho_tabla']
        # ancho genérico de columnas
        ancho_col = MEDIDAS_ACTA['ancho_col']
        # calculo ancho columna descripción
        w = 700 - dx - len(categorias) * ancho_col
        w = w - ancho_col  # resto ancho col. nº de lista

        clases_a_mostrar = self.config("clases_a_mostrar",
                                       self.data["cod_datos"])
        # Traemos solo las agrupaciones que queremos mostrar segun existe en el
        # juego de datos y segun tenemos configurado en clases_a_mostrar
        agrupaciones = Agrupacion.many(clase__in=clases_a_mostrar,
                                       sorted="orden_absoluto")
        # traemos todas las filas
        filas, caracteres_lista = self._get_datos_tabla(categorias,
                                                        agrupaciones)

        # calculo la cantidad maxima de caracteres que debe tener el nombre de
        # la agrupacion que estoy mostrando
        caracteres_tabla = MEDIDAS_ACTA['caracteres_tabla']
        cods_categorias = [cat.codigo for cat in categorias]

        # corto el largo del nombre de las agrupaciones
        remain_chars = (caracteres_tabla - caracteres_lista -
                        (len(cods_categorias) * caracteres_categoria))
        for i in range(len(filas)):
            filas[i][1] = filas[i][1][:int(remain_chars)]

        tabla = {
            "filas": filas,
            "especiales": especiales,
            "categorias": cods_categorias,
            "len_categorias": len(cods_categorias),
            "caracteres_categoria": caracteres_categoria,
            "caracteres_lista": caracteres_lista,
            "titulo_agrupaciones": _("agrupaciones"),
        }

        return tabla

    def _get_tablas_preferencias(self, max_agrupaciones=None, max_opciones=None, incluye_total=True):

        def _chunks(l, n):
            """Yield successive n-sized chunks from l."""
            for i in range(0, len(l), n):
                yield l[i:i + n]

        caracteres_categoria = 3

        dx = MEDIDAS_ACTA['margen_derecho_tabla']
        # ancho genérico de columnas
        ancho_col = MEDIDAS_ACTA['ancho_col']
        # calculo ancho columna descripción

        clases_a_mostrar = self.config("clases_a_mostrar",
                                       self.data["cod_datos"])

        # Busco primero las agrupaciones que tienen listas para este cargo/categoria
        candidaturas_prefs = Candidatura.many(cod_categoria=self._cargo_preferencias,
                                              clase='Candidato')

        # TODO ojo! Así como está funciona para Agrupaciones de tipo lista únicamente!!
        agrupaciones_cods = [c.lista.codigo for c in candidaturas_prefs]
        # Traemos solo las agrupaciones que queremos mostrar segun existe en el
        # juego de datos y segun tenemos configurado en clases_a_mostrar
        agrupaciones = Agrupacion.many(clase__in=clases_a_mostrar,
                                       sorted="orden_absoluto",
                                       codigo__in=agrupaciones_cods)

        # agrupaciones._list.sort(key=self.orden_numero)
        detalle_preferencias = self.recuento.get_preferencias_agrupadas_por_principal(
            self._cargo_preferencias)
        categoria = Categoria.one(codigo=self._cargo_preferencias)
        # traigo los datos de las listas especiales
        especiales, caracteres_categoria = self._get_datos_especiales_con_preferencias()

        cantidad_preferentes_por_lista = [
            len(detalle_preferencias[i]) for i in detalle_preferencias]
        default_opciones = 100000  # numero excesivamente alto para que tome todas las opciones
        # numero excesivamente alto para que tome todas las agrupaciones
        default_agrupaciones = 100000
        columna_total = 1 if incluye_total else 0
        max_opciones_en_lista = max(cantidad_preferentes_por_lista) + columna_total if len(
            cantidad_preferentes_por_lista) > 0 else default_opciones
        if not max_agrupaciones:
            max_agrupaciones = default_agrupaciones
        if not max_opciones:
            max_opciones = max_opciones_en_lista

        offset = 0
        tablas = []
        numero_de_tabla = 0
        for i, grupo_agrup in enumerate(
                _chunks(agrupaciones, max_agrupaciones)):
            # A diferencia de
            filas, caracteres_lista = self._get_datos_tabla_adicional(
                categoria, detalle_preferencias, grupo_agrup,
                max_agrupaciones, offset)

            nro_ordenes = []
            for j in range(len(grupo_agrup)):
                nro_ordenes.append(j+1)

            numero_de_tabla += i
            tabla = {
                "filas": filas[:max_agrupaciones],
                "especiales": [],
                "categorias": nro_ordenes,
                "len_categorias": len(nro_ordenes),
                "caracteres_categoria": caracteres_categoria,
                "caracteres_lista": caracteres_lista,
                "texto_encabezado": _("texto_tabla_pref"),
                "offset_agrupaciones": offset,
                "numero": numero_de_tabla,
                "resaltar_ultima_columna": False
            }
            if self.config('transponer_tabla_grupos_con_preferencias'):
                grupos_de_opciones = list(
                    range(0, max_opciones_en_lista, max_opciones))
                for grupo_opcion_idx, from_opcion in enumerate(grupos_de_opciones):
                    tabla["numero"] = numero_de_tabla
                    tabla["offset_agrupaciones"] = offset
                    # Para que en la imagen se resalte la columna de totales
                    tabla["resaltar_ultima_columna"] = grupo_opcion_idx == len(
                        grupos_de_opciones) - 1
                    tabla_transpuesta = self._transponer_tabla_preferentes(
                        deepcopy(tabla), desde=from_opcion, hasta=from_opcion+max_opciones)
                    tablas.append(tabla_transpuesta)
                    offset += len(grupo_agrup)
                    numero_de_tabla += 1

            else:
                tablas.append(tabla)
                offset += len(grupo_agrup)

        tablas[-1]["especiales"] = especiales

        return tablas

    def _transponer_tabla_preferentes(self, tabla_a_transponer, desde=0, hasta=-1):
        """Recibe una tabla y la transpone. Muta la tabla recibida. Asegurarse
        que recibe una copia de la tabla"""

        # Credits:
        # https://www.codegrepper.com/code-examples/python/transpose+matrix+in+python+without+numpy
        def transpose(matrix):
            rows = len(matrix)
            columns = len(matrix[0])
            transposed_matrix = []
            for j in range(columns):
                row = []
                for i in range(rows):
                    row.append(matrix[i][j])
                transposed_matrix.append(row)
            return transposed_matrix

        transposed_table = transpose(tabla_a_transponer["filas"][1:])
        old_header = tabla_a_transponer["filas"][0]
        new_first_row = transposed_table[0]
        header_to_first_column = [[old_header[idx], *values[desde:hasta]]
                                  for idx, values in enumerate(transposed_table[1:])]
        tabla_a_transponer["filas"] = [
            new_first_row[desde:hasta], *header_to_first_column]
        tabla_a_transponer['texto_encabezado'] = "LI/OPC"
        tabla_a_transponer["categorias"] = new_first_row[desde:hasta]
        tabla_a_transponer["len_categorias"] = len(
            tabla_a_transponer["categorias"])
        return tabla_a_transponer

    def _get_datos_tabla_adicional(self, categoria, detalle_preferencias,
                                   agrupaciones, cant_col, offset):
        """Devuelve los datos de la tabla principal del acta.

        Argumentos:
            categoria -- Es la categoria de la cual se quiere generar una tabla
                         adicional
            datos -- Es un diccionario con los datos que se utilizan para
                     generar la tabla.
            agrupaciones -- las agrupaciones que participan en esta Ubicacion.
        """
        filas = []
        max_char = 3
        partido_omitido = False
        clases_a_mostrar = self.config("clases_a_mostrar",
                                       self.data["cod_datos"])
        colapsar_partido = self.config("colapsar_partido",
                                       self.data["cod_datos"])
        # Calcula la cantidad máxima de preferentes que hay para esta categoría
        # TODO
        #max_preferentes = max([len(detalle_preferencias[idumv].keys()) for idumv in detalle_preferencias.keys()])

        ordenes = []
        for idumv in detalle_preferencias.keys():
            ordenes.extend(detalle_preferencias[idumv].keys())
        #max_preferentes = max([len(detalle_preferencias[idumv].keys()) for idumv in detalle_preferencias.keys()])
        max_preferentes = max(ordenes)

        # Recorro todas las agrupaciones (Alianza, Partido, Lista)
        # viendo cual segun la forma de la eleccion y las configuraciones debo
        # mostrar

        for agrupacion in agrupaciones:
            # si esta la eleccion configurada para mostrar esa clase de
            # agrupacion
            clase = agrupacion.clase
            if clase in clases_a_mostrar:
                # colapso el partido si tiene una sola lista y esta habilitado
                if colapsar_partido and clase == "Partido":
                    partido_omitido = len(agrupacion.listas) == 1
                # Traigo los datos de la fila en caso de que tenga que
                # mostrarla
                if not partido_omitido or (partido_omitido and
                                           clase != "Partido"):

                    fila, chars_lista = self._get_datos_fila_adicional(
                        categoria, detalle_preferencias,
                        agrupacion, partido_omitido, max_preferentes)

                    # Las listas solo aparecen si tienen candidatos en
                    # categorias que queremos mostrar en este acta.
                    # En fila se tiene [nro_lista, preferente 1, ..., preferente N, TOTAL]
                    # fila[1:-1] --> Solo deja [pref 1, ..., pref N], si todos son '-' (no presenta candidatos)
                    # entonces no se muestra.
                    if (clase != "Lista" or not
                            all([elem == "-" for elem in fila[1:-1]])):
                        if chars_lista > max_char:
                            max_char = chars_lista

                        # no mostramos alianazas vacías
                        try:
                            if (clase == "Alianza" and
                                    filas[-1][3] == "Alianza"):
                                filas.pop(-1)
                        except IndexError:
                            pass

                        filas.append(fila)

        # Hace una transformación de la matris de columnas a filas.
        filas = [[filas[j][i] for j in range(len(filas))]
                 for i in range(len(filas[0]))]

        # Agrega el nro de orden de los candidatos desde la fila 1 a
        # la anteúltima
        for i, fila in enumerate(filas[1:len(filas) - 1]):
            filas[i+1] = [str(i+1)] + fila

        # Agrega el encabezado total a la última fila
        filas[-1] = [_("texto_total")] + filas[-1]

        return filas, max_char

    def _get_datos_fila_adicional(self, categoria, detalle_preferencias,
                                  agrupacion, partido_omitido, cant_col):
        """Devuelve los datos de la tabla principal del acta.
        """
        # primero vamos a averiguar la indentacion que queremos ponerle a esta
        # fila en la tabla.
        if hasattr(agrupacion, "numero"):
            numero = str(agrupacion.numero)
        else:
            numero = ""

        # Suma una fila más para los totales
        cant_col = cant_col + 1

        # armamos la base de la fila.
        fila = [numero]

        # Recorremos todas las categorias que queremos mostrar en este acta
        # buscando cuantos votos tiene cada candidato.
        filter = {
            "sorted": "orden_absoluto",
            "cod_categoria":categoria.codigo,
            "cod_lista":agrupacion.codigo
        }
        candidato = Candidatura.first(**filter)
        # Si el candidato existe vamos a buscar cuantos votos tiene y sino
        # devolvemos "-" que se transforma en una cruz en el acta
        if candidato is not None:
            resultados = detalle_preferencias.get(candidato.id_umv)
            nro_orden_actual = 1
            for nro_orden, cantidad in resultados.items():
                while nro_orden_actual < nro_orden:
                    fila.append('-')
                    nro_orden_actual += 1
                fila.append(cantidad)
                nro_orden_actual += 1

            while len(fila) < cant_col:
                fila.append('-')

            # El total lo recupero con los votos almacenados para esa categoría
            cantidad = self.recuento.get_resultados(candidato.id_umv)
            fila.append(cantidad)
        else:
            for i in range(cant_col):
                fila.append("-")
        return fila, len(numero)


class ImagenActaCTX(Imagen):
    def __init__(self, qr=None):
        """Constructor.

        Argumentos:
            data: datos para rellenar el acta.
            qr: imagen del QR.
        """
        self.template = "actas/acta_prueba_ctx.tmpl"

        self.render_template()
        self.qr = qr

    def _get_medidas(self):
        """Devuelve las medidas del acta."""

        alto = MEDIDAS_ACTA["alto_recuento"]

        medidas = {
            "width": MEDIDAS_ACTA["ancho"],
            "height": alto
        }
        return medidas

    def generate_data(self):
        """Genera todos los datos que vamos a necesitar para armar el acta."""
        medidas = self._get_medidas()

        data = {
            "colores": COLORES,
            "verificador": self._get_verificador(),
            "medidas": medidas,
            "width": medidas['width'],
            "height": medidas['height'],
            "i18n": self._get_i18n(),
            "qr": self._get_qr(medidas['width'])
        }

        self.data = data

        return data

    def _get_i18n(self):

        textos = {
            "texto_acta_prueba_ctx_1": _("texto_acta_prueba_ctx_1"),
            "texto_acta_prueba_ctx_2": _("texto_acta_prueba_ctx_2"),
            "texto_acta_prueba_ctx_3": _("texto_acta_prueba_ctx_3")

        }

        return textos

    def _get_qr(self, width):
        """Devuelve los datos del QR para el template."""
        key = "qr_recuento"
        pos_x, pos_y, pos_w, pos_h = MEDIDAS_ACTA[key]
        qr = [width - pos_x, pos_y, self.qr, pos_w, pos_h]

        return qr

    def _get_verificador(self):
        """Devuelve los datos del verificador para el template."""
        # muestro imagen verificador y corro margen superior hacia abajo
        verif_x, verif_y = MEDIDAS_ACTA["verificador"]
        img_verif = join(PATH_IMAGENES_VARS, 'verificador_alta.png')
        img_verif = self._get_img_b64(img_verif)

        return (verif_x, verif_y, img_verif)
