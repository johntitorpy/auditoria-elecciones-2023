from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES
from msa.core.data.candidaturas import Agrupacion, Categoria, Candidatura
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE

from msa.core.documentos.actas import Recuento


class TablaConPreferentes(Imagen):
    def __init__(
        self,
        recuento: Recuento,
        x: int = 0,
        y: int = 0,
        max_agrupaciones: int = None,
        max_opciones: int = None,
        incluye_total: bool = None,
        clases_a_mostrar: "list[str]" = None,
        transponer_tablas: bool = None,
    ) -> None:
        super().__init__()
        self._x = x
        self._y = y
        self._recuento = recuento
        self._width = 0
        self._height = 0

        if self._recuento.grupo_cat is None:
            raise Exception(
                "La tabla de preferencias NO acepta un recuento SIN grupo de categorías especificado."
            )

        if len(Categoria.many(id_grupo=self._recuento.grupo_cat)) > 1:
            raise Exception(
                "La tabla de preferencias solo acepta 1 grupo de categorias/cargos."
            )

        if Categoria.one(id_grupo=self._recuento.grupo_cat, preferente=True) is None:
            raise Exception(
                "La categoría del recuento no tiene un cargo con preferencias."
            )

        self._categoria: Categoria = Categoria.one(
            id_grupo=self._recuento.grupo_cat, preferente=True
        )

        self._candidaturas_preferentes: "list[Candidatura]" = Candidatura.many(
            cod_categoria=self._categoria.codigo, clase="Candidato"
        )

        self._candidaturas_preferentes_id_umv_indexed = {
            c.id_umv: c for c in self._candidaturas_preferentes
        }

        self._detalle_preferencias = (
            self._recuento.get_preferencias_agrupadas_por_principal(
                self._categoria.codigo
            )
        )

        if max_agrupaciones is not None:
            self._max_agrupaciones = max_agrupaciones
        else:
            self._max_agrupaciones = self.config(
                "max_agrupaciones", self._recuento.mesa.codigo
            )

        if max_opciones is not None:
            self._max_opciones = max_opciones
        else:
            self._max_opciones = self.config("max_opciones", self._recuento.mesa.codigo)

        if incluye_total is not None:
            self._incluye_total = incluye_total
        else:
            self._incluye_total = self.config(
                "incluye_total", self._recuento.mesa.codigo
            )

        if clases_a_mostrar is not None:
            self._clases_a_mostrar = clases_a_mostrar
        else:
            self._clases_a_mostrar = self.config(
                "clases_a_mostrar", self._recuento.mesa.codigo
            )

        if transponer_tablas is not None:
            self._transponer_tablas = transponer_tablas
        else:
            self._transponer_tablas = self.config(
                "transponer_tabla_grupos_con_preferencias", self._recuento.mesa.codigo
            )

        self.template = "actas/tabla_grupos_con_preferentes.tmpl"
        self.render_template()

    @forzar_idioma(DEFAULT_LOCALE)
    def generate_data(self):

        # Reinicializa los tamaños
        self._width = 0
        self._height = 0

        data = {
            "x": self._x,
            "y": self._y,
            "i18n": self._get_i18n(),
            "colores": COLORES,
            "medidas": self._get_medidas(),
        }

        if self._transponer_tablas:
            data["tablas"] = self._get_tablas_preferencias_transpuestas()
        else:
            data["tablas"] = self._get_tablas_preferencias()
        return data

    def _get_i18n(self):
        textos = {}

        return textos

    @staticmethod
    def _get_medidas():
        data = {
            "alto_linea_tabla_preferentes": MEDIDAS_ACTA[
                "alto_linea_tabla_preferentes"
            ],
            "alto_encabezado_tabla_preferencias": MEDIDAS_ACTA[
                "alto_encabezado_tabla_preferencias"
            ],
        }

        return data

    def _get_datos_fila_adicional(self, agrupacion: Agrupacion, cant_col):
        """Devuelve los datos de la tabla principal del acta."""
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
            "cod_categoria": self._categoria.codigo,
            "cod_lista": agrupacion.codigo,
        }
        candidato = Candidatura.first(**filter)
        # Si el candidato existe vamos a buscar cuantos votos tiene y sino
        # devolvemos "-" que se transforma en una cruz en el acta
        if candidato is not None:
            resultados = self._detalle_preferencias.get(candidato.id_umv)
            nro_orden_actual = 1
            for id_umv_preferente, cantidad in resultados.items():
                preferente = self._candidaturas_preferentes_id_umv_indexed[
                    id_umv_preferente
                ]
                while nro_orden_actual < preferente.nro_orden:
                    fila.append("-")
                    nro_orden_actual += 1
                fila.append(cantidad)
                nro_orden_actual += 1

            while len(fila) < cant_col:
                fila.append("-")

            # El total lo recupero con los votos almacenados para esa categoría
            cantidad = self._recuento.get_resultados(candidato.id_umv)
            fila.append(cantidad)
        else:
            for i in range(cant_col):
                fila.append("-")
        return fila, len(numero)

    def _get_datos_tabla_adicional(self, agrupaciones: "list[Agrupacion]"):
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

        colapsar_partido = self.config("colapsar_partido", self._recuento.mesa.codigo)

        ordenes = []
        max_preferentes = 0
        for idumv in self._detalle_preferencias.keys():
            ordenes.extend([
                self._candidaturas_preferentes_id_umv_indexed[
                    id_umv_preferente
                ].nro_orden
                for id_umv_preferente in self._detalle_preferencias[idumv].keys()
            ])
        max_preferentes = max(ordenes)
        # Recorro todas las agrupaciones (Alianza, Partido, Lista)
        # viendo cual segun la forma de la eleccion y las configuraciones debo
        # mostrar

        for agrupacion in agrupaciones:
            # si esta la eleccion configurada para mostrar esa clase de
            # agrupacion
            clase = agrupacion.clase
            if clase in self._clases_a_mostrar:
                # colapso el partido si tiene una sola lista y esta habilitado
                if colapsar_partido and clase == "Partido":
                    partido_omitido = len(agrupacion.listas) == 1
                # Traigo los datos de la fila en caso de que tenga que
                # mostrarla
                if not partido_omitido or (partido_omitido and clase != "Partido"):
                    fila, chars_lista = self._get_datos_fila_adicional(
                        agrupacion, max_preferentes
                    )
                    # Las listas solo aparecen si tienen candidatos en
                    # categorias que queremos mostrar en este acta.
                    # En fila se tiene [nro_lista, preferente 1, ..., preferente N, TOTAL]
                    # fila[1:-1] --> Solo deja [pref 1, ..., pref N], si todos son '-' (no presenta candidatos)
                    # entonces no se muestra.
                    if clase != "Lista" or not all(
                        [elem == "-" for elem in fila[1:-1]]
                    ):
                        if chars_lista > max_char:
                            max_char = chars_lista

                        # no mostramos alianazas vacías
                        try:
                            if clase == "Alianza" and filas[-1][3] == "Alianza":
                                filas.pop(-1)
                        except IndexError:
                            pass
                        filas.append(fila)

        # Hace una transformación de la matris de columnas a filas.
        filas = [[filas[j][i] for j in range(len(filas))] for i in range(len(filas[0]))]

        # Agrega el nro de orden de los candidatos desde la fila 1 a
        # la anteúltima
        for i, fila in enumerate(filas[1 : len(filas) - 1]):
            filas[i + 1] = [str(i + 1)] + fila

        # Agrega el encabezado total a la última fila
        filas[-1] = [_("texto_total")] + filas[-1]

        return filas, max_char

    @staticmethod
    def _chunks(l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i : i + n], i, i + n

    def _get_tablas_preferencias(self):
        agrupaciones_cods = [c.lista.codigo for c in self._candidaturas_preferentes]

        # Traemos solo las agrupaciones que queremos mostrar segun existe en el
        # juego de datos y segun tenemos configurado en clases_a_mostrar
        agrupaciones = Agrupacion.many(
            clase__in=self._clases_a_mostrar,
            sorted="orden_absoluto",
            codigo__in=agrupaciones_cods,
        )

        tablas = []
        numero_de_tabla = 0
        for i, (grupo_agrup, start, end) in enumerate(
            TablaConPreferentes._chunks(agrupaciones, self._max_agrupaciones)
        ):
            filas, caracteres_lista = self._get_datos_tabla_adicional(grupo_agrup)

            numero_de_tabla += i
            tabla = {
                "filas": filas,
                "agrupaciones": grupo_agrup,
                "caracteres_categoria": len(str(self._recuento.boletas_contadas())),
                "caracteres_lista": caracteres_lista,
                "texto_encabezado": _("texto_tabla_pref"),
                "numero": numero_de_tabla,
                "resaltar_ultima_columna": False,
            }

            tablas.append(tabla)

            # Se actualiza el height segun la nueva tabla generada
            self._height += (
                self._get_medidas()["alto_encabezado_tabla_preferencias"]
                + len(filas) * self._get_medidas()["alto_linea_tabla_preferentes"]
            )

        # Resto al height una linea de tabla dado que las lineas extras blancas
        # son solo entre tablas.
        self._height -= self._get_medidas()["alto_linea_tabla_preferentes"]

        return tablas

    @staticmethod
    def _transpose(matrix):
        rows = len(matrix)
        columns = len(matrix[0])
        transposed_matrix = []
        for j in range(columns):
            row = []
            for i in range(rows):
                row.append(matrix[i][j])
            transposed_matrix.append(row)
        return transposed_matrix

    def _get_tablas_preferencias_transpuestas(self):
        agrupaciones_cods = set(c.lista.codigo for c in self._candidaturas_preferentes)

        # Traemos solo las agrupaciones que queremos mostrar segun existe en el
        # juego de datos y segun tenemos configurado en clases_a_mostrar
        agrupaciones = Agrupacion.many(
            clase__in=self._clases_a_mostrar,
            sorted="orden_absoluto",
            codigo__in=agrupaciones_cods,
        )

        # Obtengo los datos de todas las agrupaciones
        (
            filas_all_agrupaciones,
            caracteres_lista_all_agrupaciones,
        ) = self._get_datos_tabla_adicional(agrupaciones)

        # Agrega la columna de descripciones vacía para que la transposicion
        # se haga correctamente.
        filas_all_agrupaciones[0].insert(0, "")

        numeros_de_listas = filas_all_agrupaciones[0]

        tablas = []
        numero_de_tabla = 0
        # Obtengo los chunks quitando la fila de numeros de lista y la de totales, que seran
        # agregadas luego de trasponer la tabla
        for i, (filas_grupo, start, end) in enumerate(
            TablaConPreferentes._chunks(filas_all_agrupaciones[1:], self._max_opciones)
        ):
            # Inserto la fila de numeros de lista antes de trasponer
            filas_grupo.insert(0, numeros_de_listas)

            # Actualizo el valor de fin cuando se encuentra en el ultimo chunk
            if end > (len(filas_all_agrupaciones) - 2):
                end = len(filas_all_agrupaciones) - 1

            filas_grupo_traspuesta = TablaConPreferentes._transpose(filas_grupo)

            # Quita el primer elemento insertado para que la transposicion se haga
            # correctamente ya que no se necesita para renderizar la tabla.
            filas_grupo_traspuesta[0].pop(0)

            ordenes = [{"codigo": x} for x in range(start + 1, end + 1)]

            # caracteres_categoria determina la cantidad de caracteres que debe tener
            # una columna en la tabla para que se puedan ver los valores correctamente
            caracteres_categoria_segun_boletas = len(
                str(self._recuento.boletas_contadas())
            )
            caracteres_categoria_segun_ordenes = max(
                [len(str(cod_cat)) for cod_cat in range(start + 1, end + 1)]
            )
            caracteres_categoria_segun_minimo = self.config(
                "min_caracteres_categoria", self._recuento.mesa.codigo
            )

            caracteres_categoria = max(
                caracteres_categoria_segun_boletas,
                caracteres_categoria_segun_ordenes,
                caracteres_categoria_segun_minimo,
            )

            tabla = {
                "filas": filas_grupo_traspuesta,
                "agrupaciones": ordenes,
                "caracteres_categoria": caracteres_categoria,
                "caracteres_lista": caracteres_lista_all_agrupaciones,
                "texto_encabezado": _("texto_tabla_preferencias_transpuesta"),
                "numero": numero_de_tabla,
                "resaltar_ultima_columna": False,
            }

            tablas.append(tabla)
            numero_de_tabla += 1

            # Se actualiza el height segun la nueva tabla generada
            self._height += (
                self._get_medidas()["alto_encabezado_tabla_preferencias"]
                # Resto al height una linea de tabla dado que las lineas extras blancas
                # son solo entre tablas.
                + (
                    (len(filas_grupo_traspuesta) - 1)
                    * self._get_medidas()["alto_linea_tabla_preferentes"]
                )
            )

        # Con la tabla transpuesta, la ultima tabla resalta la ultima columna.
        tablas[-1]["resaltar_ultima_columna"] = True

        return tablas

    def get_heigth(self):
        return self._height
