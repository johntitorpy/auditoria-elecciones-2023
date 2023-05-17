# -*- coding: utf-8 -*-
""" Modulo con las clases para manejo de datos de las candidaturas."""
from random import shuffle

from ojota import Ojota, OjotaSet, Relation
from ojota.base import get_current_data_code, current_data_code
from ojota.sources import JSONSource

from msa.core.data.constants import (NOMBRE_JSON_AGRUPACIONES,
                                     NOMBRE_JSON_BOLETAS,
                                     NOMBRE_JSON_CANDIDATURAS,
                                     NOMBRE_JSON_CATEGORIAS)


class EleccionSet(OjotaSet):

    """Un OjotaSet adaptado a las necesidades de Voto."""

    def to_dict(self):
        """Devuelve una lista de diccionarios con los datos del OjotaSet."""
        return [elem.to_dict() for elem in self.all()]

    def all(self):
        """Devuelve todos los elementos del Set."""
        return self.many()

    def shuffle(self):
        """Mezcla los elementos del Set."""
        shuffle(self._list)


class CandidaturaBase(Ojota):
    data_in_root = False
    queryset_type = EleccionSet
    data_source = JSONSource(create_empty=False)

    @property
    def texto_asistida(self):
        """
        Property que devuelve el texto asistida si esta especificado y sino el
        nombre.
        """
        if hasattr(self, "nombre"):
            ret = self.nombre
            if hasattr(self, "asistida") and self.asistida is not None:
                ret = self.asistida
        else:
            ret = None
        return ret

    def to_dict(self):
        dict_ = Ojota.to_dict(self)
        dict_["texto_asistida"] = self.texto_asistida
        return dict_


class Categoria(CandidaturaBase):

    """Categoria de candidatos a elegir."""

    default_order = "posicion"
    pk_field = "codigo"
    queryset_type = EleccionSet
    plural_name = NOMBRE_JSON_CATEGORIAS
    required_fields = ("nombre", "posicion", "consulta_popular", "adhiere",
                       "asistida")

    def __str__(self):
        """Representacion del objeto. Codigo y nombre de la Candidatura."""
        return "%s - %s" % (self.codigo, self.nombre)

    def get_hijas(self):
        """Devuelve las Categorias hijas de esta Categoria si es que la hay."""
        return Categoria.many(adhiere=self.codigo, sorted="posicion")

    @property
    def posee_tachas(self):
        return hasattr(self, "max_tachas") and self.max_tachas > 0

    @property
    def posee_preferencias(self):
        return hasattr(self, "max_preferencias") and self.max_preferencias > 0

    @property
    def precandidato(self):
        """Indica si es un precandidato."""
        return self.posicion <= 5


class Candidatura(CandidaturaBase):

    """Clase base de todos los Objetos de candidaturas."""

    plural_name = NOMBRE_JSON_CANDIDATURAS
    default_order = "id_umv"
    pk_field = "id_umv"
    required_fields = ("clase", "nombre", "id_candidatura", "orden_absoluto")
    categoria = Relation('cod_categoria', Categoria)

    @property
    def lista(self):
        return Lista.one(self.cod_lista)

    @property
    def partido(self):
        ret = None
        if hasattr(self, "cod_partido"):
            ret = Partido.one(self.cod_partido)

        return ret

    @property
    def candidatos_secundarios(self):
        ret = []
        if hasattr(self, "secundarios") and len(self.secundarios)>0:
            ret = [Candidatura(
                    id_umv=-1,
                    clase="Candidato",
                    nombre=nombre,
                    id_candidatura=-1,
                    orden_absoluto=0,
                    cod_categoria=self.cod_categoria,
                    cod_lista=self.cod_lista)
                   for nombre in self.secundarios]
        elif self.categoria.posee_preferencias:
            ret = self.many(clase="Candidato", cod_categoria=self.cod_categoria, cod_lista=self.cod_lista)
        return ret

    @property
    def es_blanco(self):
        return self.clase == "Blanco"

    @classmethod
    def get_blanco(cls, cod_categoria):
        return cls.one(clase="Blanco", cod_categoria=cod_categoria)

    @classmethod
    def blancos(self):
        return self.many(clase="Blanco")

    @classmethod
    def especiales(self):
        return self.many(clase="Especial")

    @classmethod
    def seleccionables(cls, cod_categoria=None, sort=None):
        filter = {
            "clase__in": ("Blanco", "Candidato")
        }
        if cod_categoria is not None:
            if type(cod_categoria) == str:
                filter["cod_categoria"] = cod_categoria
            else:
                filter["cod_categoria__in"] = cod_categoria

        if sort is not None:
            filter["sorted"] = sort

        return cls.many(**filter)

    @classmethod
    def candidatos_principales(self):
        """Devuelve los id_umv de los candidatos principales"""
        principales = []
        for categoria in Categoria.many(sorted="posicion"):
            for lista in Lista.many(sorted='codigo'):
                candidato = self.candidato_principal(categoria.codigo, lista.codigo)
                if(candidato is not None):
                    principales.append(candidato)
        return principales

    @classmethod
    def candidato_principal(self, cod_categoria, cod_lista):
        """Devuelve los candidatos principales"""
        filter = {
            "sorted": "orden_absoluto",
            "cod_categoria":cod_categoria,
            "cod_lista":cod_lista
        }
        candidato = Candidatura.first(**filter)
        if candidato:
            return candidato
        else:
            return None
    @property
    def principal(self):
        """
        Devuelve el candidato principal de una candidatura
        """
        return self.candidato_principal(self.cod_categoria, self.cod_lista)

    @classmethod
    def tachas(self, id_umv=None):
        if id_umv is None:
            candidatos = self.many(clase="Candidato", habilitar_tachas=True)
        else:
            candidatos = self.many(
                clase="Candidato", id_umv=id_umv, habilitar_tachas=True)

        tachas = []
        for candidato_ppal in candidatos:
            tachas += \
                [candidato_ppal] + candidato_ppal.candidatos_secundarios
        return tachas

    @classmethod
    def preferencias(self, id_umv=None):
        if id_umv is None:
            candidatos = self.many(clase="Candidato", posee_preferencias=True)
        else:
            candidato = self.one(id_umv=id_umv)
            filter = {"clase": "Candidato"}
            filter['cod_categoria'] = candidato.cod_categoria
            filter['cod_lista'] = candidato.cod_lista
            filter['sorted'] = 'nro_orden'
            candidatos = self.many(**filter)

        #preferencias = []
        #for candidato_ppal in candidatos:
        #    preferencias += \
        #        [candidato_ppal] + candidato_ppal.candidatos_secundarios
        return candidatos

    @classmethod
    def para_recuento(cls, grupo_cat=None):
        if grupo_cat is not None:
            categorias = Categoria.many(id_grupo=grupo_cat)
        else:
            categorias = Categoria.all()
        cods_cats = [categoria.codigo for categoria in categorias]
        candidatos = cls.seleccionables(cods_cats, sort="orden_absoluto")
        return candidatos

    def __str__(self):
        """Representacion del objeto. Codigo y nombre de la Candidatura."""
        return "%s - %s - %s" % (self.clase, self.id_umv, self.nombre)


class Agrupacion(CandidaturaBase):

    """Clase base de todos los Objetos de candidaturas."""

    plural_name = NOMBRE_JSON_AGRUPACIONES
    default_order = "codigo"
    pk_field = "codigo"
    required_fields = ("clase", "nombre", "color", "imagenes", "nombre",
                       "nombre_corto", "asistida")

    @classmethod
    def get_cache_name(cls):
        """Genera el nombre que vamos a usar para guardar en cache."""
        if cls.cache_name is not None:
            cache_name = '_cache_' + cls.cache_name
        else:
            cache_name = '_cache_' + cls.get_plural_name()

        if cls.prefilter is not None and "clase" in cls.prefilter:
            cache_name += "_" + cls.prefilter["clase"]

        if not cls.data_in_root and get_current_data_code():
            cache_name += '_' + get_current_data_code()

        return cache_name

    @property
    def partido(self):
        return Agrupacion.one(clase="Partido",
                              codigo=self.cod_partido)

    @property
    def alianza(self):
        return Agrupacion.one(clase="Alianza",
                              codigo=self.cod_alianza)

    @property
    def listas(self):
        filter = {"clase": "Lista"}
        if self.clase == "Alianza":
            filter['cod_alianza'] = self.codigo
        elif self.clase == "Partido":
            filter['cod_partido'] = self.codigo

        return self.many(**filter)


class Partido(Agrupacion):
    prefilter = {"clase": "Partido"}


class Lista(Agrupacion):
    prefilter = {"clase": "Lista"}

    @property
    def candidatos(self):
        """
        Property que devuelve todos los candidatos principales de esta lista,
        Incluye los candidatos adheridos a la lista.
        """
        categorias = Categoria.all()

        candidatos = []
        boleta = Boleta.one(self.codigo)
        if boleta is not None:
            for categoria in categorias:
                candidato = boleta.get_candidato(categoria.codigo)
                if candidato is not None:
                    candidatos.append(candidato)

        return candidatos


class Alianza(Agrupacion):
    prefilter = {"clase": "Alianza"}


class Boleta(Ojota):

    """Representa una boleta con cuerpos adosados como las elec tradicionales.

    Es una capa de compatibilidad para soportar adhesiones cruzadas, listas
    espejo y demas cosas que tienen mucho más sentido en el modelo analogico
    que en la BUE. Cuando no haya mas Lista Completa análoga de las elecciones
    tradicionales esto debería desaparecer.
    """
    data_in_root = False
    default_order = "codigo"
    pk_field = "codigo"
    queryset_type = EleccionSet
    data_source = JSONSource(create_empty=False)

    plural_name = NOMBRE_JSON_BOLETAS

    def __str__(self):
        """Representacion del objeto. Codigo y nombre de la Candidatura."""
        return "%s" % self.codigo

    def get_candidato(self, cod_categoria):
        """Devuelve el candidato para tal categoría para esta lista."""
        if hasattr(self, cod_categoria):
            candidato = Candidatura.one(id_umv=getattr(self, cod_categoria))
        else:
            candidato = None

        return candidato

    @property
    def lista(self):
        """Devuelve la lista de esta boleta."""
        lista = Candidatura.listas().one(self.codigo)
        return lista

    @property
    def tiene_consulta(self):
        """Identifica si la boleta tiene alguna categoría que es Consulta
        Popular."""
        ret = False
        for field in self.fields:
            cat = Categoria.one(codigo=field)
            if cat is not None and cat.consulta_popular:
                ret = True
                break

        return ret
