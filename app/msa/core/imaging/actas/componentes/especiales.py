from copy import copy

from msa.constants import COD_LISTA_BLANCO, COD_TOTAL, COD_NULO
from msa.core.data import Candidatura
from msa.core.data.candidaturas import Categoria, Agrupacion
from msa.core.documentos.actas import Recuento
from msa.core.documentos.helpers import smart_title
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.imaging import Imagen
from msa.core.imaging.constants import MEDIDAS_ACTA, COLORES, DEFAULTS_MOSTRAR_ACTA


class EspecialesActa(Imagen):
    def __init__(
        self, recuento: Recuento, mostrar=None, extra=None, x: int = 0, y: int = 0
    ) -> None:
        super().__init__()
        self.__heigt = None
        self._recuento = recuento
        self._extra = extra
        self._x = x
        self._y = y

        self._mostrar = copy(DEFAULTS_MOSTRAR_ACTA)
        if mostrar is not None:
            self._mostrar.update(mostrar)

        self.template = "actas/tabla_especiales.tmpl"
        self.render_template()
        self._load_categorias()

    def generate_data(self) -> object:
        data = {
            "x": self._x,
            "y": self._y,
            "colores": COLORES,
            "i18n": self._get_i18n(),
            "en_pantalla": self.config_vista("en_pantalla"),
            "medidas": self._get_medidas(),
            "especiales": self._get_especiales(),
        }

        self.__heigt = len(data["especiales"]) * data["medidas"]["alto_linea_tabla"]

        return data

    @forzar_idioma(DEFAULT_LOCALE)
    def _get_i18n(self) -> object:
        textos = {
            "titulo_especiales": _("titulo_especiales"),
        }
        return textos

    def _get_medidas(self) -> object:
        """Devuelve las medidas del acta"""
        categorias = self._get_categorias()
        cods_categorias = [cat.codigo for cat in categorias]

        # caracteres_categoria determina la cantidad de caracteres que debe tener
        # una columna en la tabla para que se puedan ver los valores correctamente
        caracteres_categoria_segun_boletas = len(
            str(
                self._recuento.boletas_contadas()
                + sum(self._recuento.listas_especiales.values())
            )
        )
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

        clases_a_mostrar = self.config(
            "clases_a_mostrar", self._recuento.mesa.cod_datos
        )
        agrupaciones = Agrupacion.many(
            clase__in=clases_a_mostrar, sorted="orden_absoluto"
        )
        caracteres_lista = self._get_caracteres_lista(agrupaciones)

        medidas = {
            "margin_left": MEDIDAS_ACTA["margin_left"],
            "alto_linea_tabla": MEDIDAS_ACTA["alto_linea_tabla"],
            "caracteres_categoria": caracteres_categoria,
            "caracteres_lista": caracteres_lista,
        }

        return medidas

    def _get_especiales(self):
        especiales = self._get_datos_especiales()
        return especiales

    def _load_categorias(self):
        filter = {
            "sorted": "posicion",
        }

        mostrar_adheridas = self.config(
            "mostrar_adheridas_acta", self._recuento.mesa.cod_datos
        )
        if not mostrar_adheridas:
            filter["adhiere"] = None

        if self._recuento.grupo_cat is not None:
            filter["id_grupo"] = self._recuento.grupo_cat

        self._categorias = Categoria.many(**filter)

    def _get_categorias(self):
        return self._categorias

    def _get_datos_especiales(self):
        """
        Devuelve los valores para la tabla de listas especiales.
        """
        valores_especiales = []
        for lista_esp in self._recuento.mesa.listas_especiales:
            fila = (
                lista_esp,
                _("titulo_votos_%s" % lista_esp),
                self._recuento.listas_especiales[lista_esp],
            )
            valores_especiales.append(fila)

        # Total general
        general = self._recuento.boletas_contadas()
        general += sum(self._recuento.listas_especiales.values())
        valores_especiales.append((COD_TOTAL, _("total_general"), general))

        return valores_especiales

    def _get_caracteres_lista(self, agrupaciones: "list[Agrupacion]"):
        max_char = 3
        mostrar_numero = self.config(
            "numero_lista_en_tabla", self._recuento.mesa.cod_datos
        )
        for agrupacion in agrupaciones:
            if mostrar_numero and hasattr(agrupacion, "numero") and agrupacion.numero:
                chars_lista = str(agrupacion.numero)
            else:
                chars_lista = ""

            if len(chars_lista) > max_char:
                max_char = len(chars_lista)

        return max_char

    def get_height(self):
        return self.__heigt
