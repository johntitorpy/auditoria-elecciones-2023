from msa.core.imaging.actas.componentes.tabla_sin_preferentes import TablaSinPreferentes


class TablaSinPreferentesSinBlanco(TablaSinPreferentes):

    def _get_datos_fila_blanca(self, categorias):
        return None
