from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES
from msa.core.data.candidaturas import Agrupacion, Categoria, Candidatura
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE

from msa.core.documentos.actas import Recuento


class TablaSinPreferentes(Imagen):
    def __init__(self, recuento: Recuento, x: int = 0, y: int = 0) -> None:
        super().__init__()
        self._recuento = recuento
        self._x = x
        self._y = y
        self.template = "actas/tabla_grupos_sin_preferentes.tmpl"
        self._height = 0
        self._width = 0
        self.render_template()

    def generate_data(self):
        self._height = 0
        self._width = 0

        data = {
            "x": self._x,
            "y": self._y,
            "i18n": self._get_i18n(),
            "colores": COLORES,
            "medidas": self._get_medidas(),
            "tabla": self._get_tabla_votos(),
        }
        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self):
        textos = {
            "agrupaciones": _("agrupaciones"),
        }

        return textos

    def _get_medidas(self):
        """Devuelve las medidas del acta."""

        medidas = {
            "alto_linea_tabla": MEDIDAS_ACTA["alto_linea_tabla"],
            "alto_encabezado": MEDIDAS_ACTA["alto_encabezado"],
            "separacion_especiales": MEDIDAS_ACTA["separacion_especiales"],
        }
        return medidas

    def _get_categorias(self) -> "list[Categoria]":
        # Ordenamos siempre por la posicion de la Categoria.
        filter = {"sorted": "posicion", "preferente": False}

        # Quizas queremos omitir las categorias adheridas, como en algunas
        # elecciones en las que el vicegobernador es un cargo que adhiere al de
        # gobernador.
        mostrar_adheridas = self.config(
            "mostrar_adheridas_acta", self._recuento.mesa.cod_datos
        )
        if not mostrar_adheridas:
            filter["adhiere"] = None

        # En caso de querer generar la tabla con un solo grupo de categorias
        if self._recuento.grupo_cat is not None:
            filter["id_grupo"] = self._recuento.grupo_cat

        # Traemos todas las categorias con el filtro que acabamos de armar
        categorias = Categoria.many(**filter)

        return categorias

    def _get_datos_fila_blanca(self, categorias):
        """Devuelve los datos de la fila de votos en blanco.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
        """
        mostrar_numero = self.config(
            "numero_lista_en_tabla", self._recuento.mesa.cod_datos
        )
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
                resultado = self._recuento.get_resultados(candidato.id_umv)
                # muestro la cantidad de blancos
                cantidad_blancos += 1
            fila.append(resultado)
        # si tengo candidatos blancos tenemos que mostar la fila de blancos.
        if not cantidad_blancos:
            fila = None

        return fila

    def _get_datos_fila(self, categorias, agrupacion: Agrupacion, partido_omitido):
        """Devuelve los datos de la tabla principal del acta.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
            agrupacion -- la agrupacion de la que estamos mostrando la tabla
        """
        # primero vamos a averiguar la indentacion que queremos ponerle a esta
        # fila en la tabla.
        clases_a_mostrar = self.config(
            "clases_a_mostrar", self._recuento.mesa.cod_datos
        )
        mostrar_numero = self.config(
            "numero_lista_en_tabla", self._recuento.mesa.cod_datos
        )

        mostrar_nombre_corto = self.config(
            "mostrar_nombre_corto", self._recuento.mesa.codigo
        )

        indentacion = clases_a_mostrar.index(agrupacion.clase)
        # si el partido no esta omitido vamos a ponerle profundidad.
        if not partido_omitido:
            nombre = " " * indentacion
            if not mostrar_nombre_corto:
                nombre += agrupacion.nombre
            else:
                nombre += agrupacion.nombre_corto
        # sino el nombre pasa de largo y queda el que está.
        else:
            if not mostrar_nombre_corto:
                nombre = agrupacion.partido.nombre
            else:
                nombre = agrupacion.partido.nombre_corto

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
            candidato = Candidatura.one(
                cod_lista=agrupacion.codigo, cod_categoria=categoria.codigo
            )
            # Si el candidato existe vamos a buscar cuantos votos tiene y sino
            # devolvemos "-" que se transforma en una cruz en el acta
            if candidato is not None:
                votos = self._recuento.get_resultados(candidato.id_umv)
            else:
                votos = "-"
            fila.append(votos)

        return fila, len(numero)

    def _get_datos_tabla(self, categorias, agrupaciones: "list[Agrupacion]"):
        """Devuelve los datos de la tabla principal del acta.

        Argumentos:
            categorias -- las categorias que queremos mostrar en la tabla.
            agrupaciones -- las agrupaciones que participan en esta Ubicacion.
        """
        filas = []
        max_char = 3
        partido_omitido = False
        clases_a_mostrar = self.config(
            "clases_a_mostrar", self._recuento.mesa.cod_datos
        )
        colapsar_partido = self.config(
            "colapsar_partido", self._recuento.mesa.cod_datos
        )
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
                if not partido_omitido or (partido_omitido and clase != "Partido"):
                    fila, chars_lista = self._get_datos_fila(
                        categorias, agrupacion, partido_omitido
                    )
                    # Las listas solo aparecen si tienen candidatos en
                    # categorias que queremos mostrar en este acta.
                    if clase != "Lista" or not all([elem == "-" for elem in fila[3:]]):
                        if chars_lista > max_char:
                            max_char = chars_lista

                        # no mostramos alianazas vacías
                        try:
                            if clase == "Alianza" and filas[-1][3] == "Alianza":
                                filas.pop(-1)
                        except IndexError:
                            pass

                        filas.append(fila)

        # Vemos si tenemos votos en blanco para agregar
        fila_blanca = self._get_datos_fila_blanca(categorias)
        if fila_blanca is not None:
            filas.append(fila_blanca)

        return filas, max_char

    def _get_tabla_votos(self):
        """Construye la tabla del recuento y devuelve los datos."""

        categorias = self._get_categorias()

        clases_a_mostrar = self.config(
            "clases_a_mostrar", self._recuento.mesa.cod_datos
        )
        # Traemos solo las agrupaciones que queremos mostrar segun existe en el
        # juego de datos y segun tenemos configurado en clases_a_mostrar
        agrupaciones = Agrupacion.many(
            clase__in=clases_a_mostrar, sorted="orden_absoluto"
        )
        # traemos todas las filas
        filas, caracteres_lista = self._get_datos_tabla(categorias, agrupaciones)

        # calculo la cantidad maxima de caracteres que debe tener el nombre de
        # la agrupacion que estoy mostrando
        caracteres_tabla = MEDIDAS_ACTA["caracteres_tabla"]
        cods_categorias = [cat.codigo for cat in categorias]

        # caracteres_categoria determina la cantidad de caracteres que debe tener
        # una columna en la tabla para que se puedan ver los valores correctamente
        caracteres_categoria_segun_boletas = len(str(self._recuento.boletas_contadas()))
        caracteres_categoria_segun_codigos_categorias = max(
            [len(str(cod_cat)) for cod_cat in cods_categorias]
        )
        caracteres_categoria_segun_minimo = self.config(
            "min_caracteres_categoria", self._recuento.mesa.codigo
        )

        caracteres_categoria = max(
            caracteres_categoria_segun_boletas,
            caracteres_categoria_segun_codigos_categorias,
            caracteres_categoria_segun_minimo,
        )

        # corto el largo del nombre de las agrupaciones
        remain_chars = (
            caracteres_tabla
            - caracteres_lista
            - (len(cods_categorias) * caracteres_categoria)
        )
        for i in range(len(filas)):
            filas[i][1] = filas[i][1][: int(remain_chars)]

        tabla = {
            "filas": filas,
            "categorias": cods_categorias,
            "len_categorias": len(cods_categorias),
            "caracteres_categoria": caracteres_categoria,
            "caracteres_lista": caracteres_lista,
        }

        # Se actualiza el height segun la nueva tabla generada
        self._height += (
            self._get_medidas()["alto_encabezado"]
            + len(filas) * self._get_medidas()["alto_linea_tabla"]
        )

        return tabla

    def get_height(self):
        return self._height
