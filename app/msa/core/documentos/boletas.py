# -*- coding: utf-8 -*-
from construct import Container, RangeError

from msa.core.data.candidaturas import Categoria, Candidatura
from msa.core.data import Ubicacion
from msa.core.documentos.constants import (
    LEN_LEN_UBIC, LEN_LEN_OPC, LEN_LEN_PRE, LEN_LEN_TAC)
from msa.core.documentos.structs import struct_voto
from msa.core.exceptions import MesaIncorrecta
from msa.core.imaging.boleta import ImagenBoleta
from msa.core.i18n.decorators import forzar_idioma
from msa.core.i18n.settings import DEFAULT_LOCALE
from msa.core.packing.smart_numpacker import MAXBITS
from msa.core.imaging.imagen_prueba_equipo import ImagenPruebaEquipo
import secrets

from msa.core.logging import get_logger

logger = get_logger('boletas')

class Seleccion(object):

    """Seleccion de candidatos (voto)."""

    def __init__(self, mesa, interna=None, candidatos=None, tachas=None,
                 preferencias=None):
        self.mesa = mesa
        self.__candidatos = candidatos[:] if candidatos else []
        self.__tachas = tachas[:] if tachas else []
        self.__preferencias = preferencias if preferencias else {}
        self.interna = interna

    def elegir_candidato(self, candidato, borrar=True):
        """Guarda un candidato seleccionado. Si el cargo del candidato es con preferencias, entonces
            llama a `elegir_preferencias`.

        Argumentos:
            candidato -- un objeto Candidatura.
            borrar -- Borra todos los candidatos de esa categoria si es True
        """
        # Primero nos fijamos que el candidato no sea None
        if candidato is not None:
            # y despues buscamos que ese candidato efectivamente exista
            seleccionables = Candidatura.seleccionables()
            encontrado = seleccionables.one(id_umv=candidato.id_umv)
            if encontrado is not None:
                categoria = Categoria.one(codigo=encontrado.cod_categoria)
                if categoria.preferente:
                    self.elegir_preferencias(candidato, borrar=borrar)
                else:
                    self._elegir_candidato(candidato, borrar=borrar)
            else:
                raise ValueError
        else:
            raise ValueError
        
    def _elegir_candidato(self, candidato, borrar=True):
        if borrar:
            self.borrar_categoria(candidato.cod_categoria)
        self.__candidatos.append(candidato)

    def elegir_tachas(self, candidato, borrar=True):
        """Guarda una tacha seleccionada.

        Argumentos:
            candidato -- un objeto Candidatura.
            borrar -- Borra todos los candidatos de esa categoria si es True
        """
        # Primero nos fijamos que el candidato no sea None
        if candidato is not None:
            # y despues buscamos que ese candidato efectivamente exista
            seleccionables = [c.id_candidatura for c
                              in Candidatura.tachas()]
            categoria = candidato.categoria
            id_candidatura = candidato.id_candidatura

            if id_candidatura in seleccionables and categoria.posee_tachas:
                ingresados = [c.id_candidatura for c in self.__tachas]
                if id_candidatura not in ingresados:
                    self.__tachas.append(candidato)
            else:
                raise ValueError
        else:
            raise ValueError

    def elegir_preferencias(self, candidato, borrar=True):
        """Guarda una preferencia seleccionada.

        Argumentos:
            candidato -- un objeto Candidatura.
            borrar -- Borra todos los candidatos de esa categoria si es True
        """
        # Primero nos fijamos que el candidato no sea None
        if candidato is not None:
            categoria = candidato.categoria
            id_umv = candidato.id_umv
            if categoria.codigo not in self.__preferencias:
                self.__preferencias[categoria.codigo] = []
            if categoria.posee_preferencias:
                ingresados = [c.id_umv for c in self.__preferencias[categoria.codigo]]
                if id_umv not in ingresados:
                    self.__preferencias[categoria.codigo].append(candidato)
            else:
                raise ValueError
        else:
            raise ValueError

    def borrar_tachas(self):
        """Limpia las tachas existentes. Para empezar de 0 si hubo idas y vueltas
        en el front."""
        self.__tachas = []

    def borrar_preferencias(self):
        """Limpia las preferencias existentes."""
        self.__preferencias = {}

    def borrar_categoria(self, cod_categoria):
        """Borra los candidatos de una categoria.

        Argumentos:
            cod_categoria -- el codigo de la categoria de la que se quieren
                borrar los candidatos
        """
        remover = []
        for candidato in self.__candidatos:
            if str(candidato.cod_categoria) == str(cod_categoria):
                remover.append(candidato)
        for candidato in remover:
            self.__candidatos.remove(candidato)

    def candidato_categoria(self, cod_categoria):
        """Determina si se ha seleccionado candidato para una categoria.
           Si se eligio lo devuelve."""
        categoria = Categoria.one(codigo=cod_categoria)
        if categoria.posee_preferencias:
            candidatos = self.preferencias_elegidas(cod_categoria)
        else:
            candidatos = [c for c in self.__candidatos
                      if c.cod_categoria == cod_categoria]
        if candidatos:
            return candidatos
        else:
            return None

    def candidatos_elegidos(self):
        """Devuelve una copia de la lista con los canditatos elegidos."""
        return self.__candidatos[:]

    def tachas_elegidas(self):
        """Devuelve una copia de la lista con las tachas elegidas."""
        return self.__tachas[:]

    def preferencias_elegidas(self, cod_categoria):
        """Devuelve una copia de la lista con las preferencias elegidas."""
        if cod_categoria in self.__preferencias:
            return self.__preferencias[cod_categoria][:]
        else:
            # logger.warning(
            #     'Se pidió el listado de preferencias para una categoria ({}) que no fué cargada'
            #         .format(cod_categoria)
            # )
            return []

    def rellenar_de_blanco(self):
        """Agrega voto en blanco a las categorias que no fueron votadas."""
        for categoria in Categoria.many():
            if (self.candidato_categoria(categoria.codigo) is None and
                self.preferencias_elegidas(categoria.codigo) == []
            ):
                blanco = Candidatura.one(cod_categoria=categoria.codigo,
                                         clase="Blanco")
                if blanco is not None:
                    self.elegir_candidato(blanco)

    def a_tag(self):
        """Devuelve la informacion de la seleccion para almacenar en tag rfid.
        """
        # Generamos el largo del codigo de ubicacion de la mesa
        # Y los votos de cada categoria (lista de id_umv de candidaturas)
        votos_categorias = self._votos_categorias()
        tachas = self._tachas()
        preferencias = self._preferencias()

        ubicacion = bytes(self.mesa.cod_datos, "ascii")
        len_ubic = bytes(str(len(ubicacion)).zfill(LEN_LEN_UBIC), "ascii")
        opciones = votos_categorias
        len_opciones = bytes(str(len(opciones)).zfill(LEN_LEN_OPC), "ascii")
        len_preferencias = bytes(str(len(preferencias)).zfill(LEN_LEN_TAC), "ascii")
        len_tachas = bytes(str(len(tachas)).zfill(LEN_LEN_TAC), "ascii")

        container = Container(len_ubic=len_ubic,
                              ubicacion=ubicacion,
                              opciones=opciones,
                              len_opciones=len_opciones,
                              tachas=tachas,
                              len_tachas=len_tachas,
                              len_preferencias=len_preferencias,
                              preferencias=preferencias)
        built = struct_voto.build(container)
        return built

    def _votos_categorias(self):
        """Devuelve una lista con los votos a guardar en el tag."""
        categorias = []
        cand_ordenados = sorted(self.__candidatos,
                                key=lambda cand: cand.categoria.posicion)
        for candidato in cand_ordenados:
            # sólo guardar la clave primaria de la candidatura:
            categorias.append(candidato.id_umv)
        return categorias

    def _tachas(self):
        return [candidato.nro_orden for candidato in self.__tachas]

    def _preferencias(self):
        def _get_second_elem(iterable):
            """
            Funcion para obtener la posicion de la categoria
            """
            return iterable[1][0].categoria.posicion

        # Ordena los items de las preferencias por posición de la categoria
        prefs_by_cat_pos = sorted(self.__preferencias.items(),
                                key=_get_second_elem)

        preferencias = []

        # Ahora genero un array con todas las preferencias consecutivas
        for cat, prefs_cat in prefs_by_cat_pos:
            preferencias.extend([candidato.id_umv for candidato in prefs_cat])

        return preferencias

    @forzar_idioma(DEFAULT_LOCALE)
    def a_imagen(self, mostrar=None, svg=False):
        """Genera la imagen de la boleta."""
        imagen = ImagenBoleta(self, mostrar)
        rendered = imagen.render(svg)
        return rendered

    @forzar_idioma(DEFAULT_LOCALE)
    def tomar_datos(self, mostrar=None):
        """Devuelve los datos de selección del usuario."""
        imagen = ImagenBoleta(self, mostrar)
        data = imagen.generate_data()
        return data

    def __str__(self):
        
        str_sel = 'Categorías sin preferencias: \n'
        str_sel += '; '.join('%s: %s' % (c.cod_categoria, c.nombre)
                        for c in self.__candidatos)
        
        if self.__tachas:
            str_sel += '\nCategorías con tachas: \n'
            str_sel += '; '.join(
                [str(c.id_umv) for c in self.__tachas])
        
        if self.__preferencias:
            str_sel += '\nCategorías con preferencias: \n'
            str_sel += '; '.join(
                [categoria+':'+' '.join([p.nombre for p in preferentes]) for categoria, preferentes in self.__preferencias.items()])
        
        return str_sel

    def esta_incompleta(self):
        """Indica si alguna categoría esta como incompleta"""
        for categoria in Categoria.all():
            candidatos = self.candidato_categoria(categoria.codigo)
            if candidatos is None or len(candidatos)==0:
                return True
        return False

    @classmethod
    def desde_tag(cls, tag, mesa=None, convertir=False):
        """Devuelve una seleccion a partir de la informacion de un tag rfid.

        Args:
            mesa ( Ojota o str):
            convertir (boolean): si es True significa que hay que convertir el 
                str de la mesa en objeto de Ojota.
        """
        seleccion = None

        try:
            datos_tag = struct_voto.parse(tag)
        except RangeError:
            # Manejamos que no nos puedan meter cualquier
            datos_tag = None

        if datos_tag is not None:
            ubic = datos_tag.ubicacion.decode("utf-8")
            if mesa is not None: #  si es objeto ojota o str
                if convertir: #  si hay que convertir el str a ojota
                    mesa = Ubicacion.first(codigo=mesa)
                if mesa is not None:  # por si al convertir a ojota se obtuvo None
                    if mesa.cod_datos != ubic:
                        raise MesaIncorrecta()
                else:
                    raise MesaIncorrecta()
            else:
                # OJO: Esto trae cualquier mesa del juego de datos.
                # No importa cual porque todas las mesas del mismo juego son
                # compatibles pero no nos permite identificar de que mesa es
                # el voto.
                mesa = Ubicacion.first(cod_datos=ubic)
            mesa.usar_cod_datos()

            seleccion = Seleccion(mesa)

            sel_por_cat = {}
            # recorremos cada uno de los candidatos en el tag
            opciones = datos_tag.opciones
            if len(opciones):
                # Determina el offset (en el array de preferencias) en que se deben empezar a leer las preferencias
                # del cargo que está siendo procesado
                for id_umv in opciones:
                    if id_umv:
                        # Buscamos el candidato votado en cuestion
                        candidato = Candidatura.one(id_umv=id_umv)
                        # y lo elegimos (Si no encontró ninguno lanza un value
                        # error).
                        if candidato is None:
                            raise ValueError()
                        cod_cat = candidato.cod_categoria
                        # acumulo las opciones para la categoría:
                        sel_por_cat[cod_cat] = sel_por_cat.get(cod_cat, 0) + 1
                        max_selecciones = int(
                            candidato.categoria.max_selecciones)
                        borrar = max_selecciones == 1
                        seleccion.elegir_candidato(candidato, borrar=borrar)

                        categoria = candidato.categoria

                        if not candidato.es_blanco:
                            if categoria.posee_tachas:
                                tachas = datos_tag.tachas
                                if len(tachas) > categoria.max_tachas:
                                    raise ValueError()
                                elif len(tachas):
                                    _c_tachas = Candidatura.tachas(
                                        id_umv=candidato.id_umv)
                                    for nro_orden in tachas:
                                        for _candidato in _c_tachas:
                                            if _candidato.nro_orden == nro_orden:
                                                seleccion.elegir_tachas(_candidato)
                                                break
                                        else:
                                            # No se encontró el candidato, salgo
                                            # con error
                                            raise ValueError()


                #se agregan las preferencias
                #array con cantidad de selecciones por categoria
                #ya que la cantidad de preferencias es variable
                for id_umv in datos_tag.preferencias:
                    if id_umv:
                        candidato = Candidatura.one(id_umv=id_umv)
                        if candidato is None:
                            raise ValueError()
                        seleccion.elegir_preferencias(candidato)
                        cod_cat = candidato.cod_categoria
                        # acumulo las opciones para la categoría:
                        sel_por_cat[cod_cat] = sel_por_cat.get(cod_cat, 0) + 1

                if len(list(sel_por_cat.keys())) != len(Categoria.all()):
                    # caso en el que la canditad de categorias votadas sea
                    # diferente que la cantidad de categorias
                    seleccion = None
                else:
                    # aca verificamos que la cantidad de candidatos por
                    # categoria este entre el min y max de preferencias
                    # que esperamos
                    for cod_categoria, cantidad in list(sel_por_cat.items()):
                        categoria = Categoria.one(cod_categoria)
                        if categoria.posee_preferencias:
                            min_selec = int(categoria.min_preferencias)
                            max_selec = int(categoria.max_preferencias)
                            if (categoria is None or cantidad < min_selec 
                                or cantidad > max_selec
                            ):
                                seleccion = None
                                break
                        else:
                            max_selec = int(categoria.max_selecciones)
                            if categoria is None or cantidad > max_selec:
                                seleccion = None
                                break

        return seleccion


class PruebaEquipo(object):
    """Clase que implementa las actas de prueba de equipo.

    Args:
        Acta ([type]): [description]

    Raises:
        RuntimeError: [description]

    Returns:
        [type]: [description]
    """

    logger = get_logger("boletas")
    # usar la configuración predeterminada para empaquetamiento de numeros:
    clase_acta = "PDE "  # prefijo para QR y serialización

    def __init__(self, contenido=[0, 0, 0, 0, 0, 0, 0, 0], nro=0):
        self._contenido = contenido
        self._nro = nro
        self.hora = None

    def a_tag(self, free_chip_mem=MAXBITS):
        """Devuelve la informacion del recuento para almacenar en tag rfid."""
        return secrets.token_bytes(free_chip_mem)

    @forzar_idioma(DEFAULT_LOCALE)
    def a_imagen(self, svg=False):
        """Genera la imagen de la boleta."""
        imagen = ImagenPruebaEquipo(self)
        rendered = imagen.render(svg)
        return rendered

    @property
    def timestamp(self):
        """Marca de tiempo (horas, minutos, segundos)"""
        # rellenar campos faltantes
        timestamp = self.hora or {}
        for substruct in struct_timestamp.subcon.subcons:
            if not substruct.name in timestamp:
                timestamp[substruct.name] = 0
        return timestamp
