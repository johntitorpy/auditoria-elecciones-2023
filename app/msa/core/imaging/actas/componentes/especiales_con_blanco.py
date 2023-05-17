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
from msa.core.imaging.actas.componentes.especiales import EspecialesActa


class EspecialesConBlancoActa(EspecialesActa):

    def __init__(self, recuento: Recuento, mostrar=None, extra=None, x: int = 0, y: int = 0) -> None:
        super().__init__(recuento, mostrar, extra, x, y)

    def _get_datos_especiales(self):
        especiales = super()._get_datos_especiales()
        fila_blanca = self._get_datos_fila_blanca()
        for i in range(len(especiales)):
            if fila_blanca and especiales[i][0] == self.config(
                "blanco_en_especiales_despues_de", self._recuento.mesa.cod_datos
            ):
                especiales.insert(i + 1, fila_blanca)

        return especiales

    def _get_datos_fila_blanca(self) -> object:
        """
        Devuelve los datos de la fila de votos en blanco.
        Args:
            categorias -- las categorias que queremos mostrar en la tabla.
        """
        if len(self._get_categorias()) <= 0:
            return None
        elif len(self._get_categorias()) > 1:
            raise Exception(
                "No se puede agregar voto en blanco a la tabla de especiales cuando el acta tiene mas de un cargo"
            )
        elif len(self._get_categorias()) == 1:
            categoria = self._get_categorias()[0]
            fila = [COD_LISTA_BLANCO, _("votos_en_blanco")]

            candidato = Candidatura.get_blanco(categoria.codigo)

            if candidato:
                resultado = self._recuento.get_resultados(candidato.id_umv)
            else:
                resultado = "-"

            fila.append(resultado)
            return fila