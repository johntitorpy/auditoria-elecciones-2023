"""Maneja la sumatoria de votos del escrutinio."""
from collections import OrderedDict
from msa.core.data.candidaturas import Candidatura, Categoria, Lista

class Pizarra():

    """Clase que maneja la sumatoria de votos del escrutinio."""

    def __init__(self):
        """Constructor de la Pizarra.

        Es una representacion de la Pizarra Fisica que usan las autoridades de
        mesa en las elecciones tradicionales.
        """
        self.__resultados = {}

        # Cuenta la cantidad de tachas que recibe una lista, por cada categoría..
        self.__tachas = {}

        # Cuenta la cantidad de preferencias que recibe una lista, por cada categoría..
        self.__preferencias = {}

        # Cuenta la cantidad de tachas que recibe cada candidato, por cada categoría.
        self.__detalle_tachas = {}

        # Cuenta la cantidad de preferencias que recibe cada candidato, por cada categoría.
        self.__detalle_preferencias = {}

        self.__candidatos_principales = Candidatura.candidatos_principales()
        self.__candidaturas_seleccionables = Candidatura.seleccionables(sort='nro_orden')
        
        for candidatura in self.__candidaturas_seleccionables:
            
            categoria = candidatura.categoria
            
            # Inicializa __preferencias en caso de no haberse procesado la 
            # categoría del candidato.
            if categoria.posee_preferencias and categoria.codigo not in self.__preferencias:
                self.__preferencias[categoria.codigo] = {}

            # Inicializa __tachas en caso de no haberse procesado la 
            # categoría del candidato.
            if categoria.posee_tachas and categoria.codigo not in self.__tachas:
                self.__tachas[categoria.codigo] = {}
            
            # Inicializa __detalle_preferencias en caso de no haberse procesado la 
            # categoría del candidato.
            if categoria.posee_preferencias and categoria.codigo not in self.__detalle_preferencias:
                self.__detalle_preferencias[categoria.codigo] = OrderedDict()

            # Inicializa __detalle_tachas en caso de no haberse procesado la 
            # categoría del candidato.
            if categoria.posee_tachas and categoria.codigo not in self.__detalle_tachas:
                self.__detalle_tachas[categoria.codigo] = OrderedDict()


            # Si es el primer candidato de la lista, se inicializan los resultados en 0.
            # El primer candidato de la lista identifica la lista y se usa para contar los 
            # votos/preferencias/tachas totales que recibio la lista.
            if candidatura in self.__candidatos_principales or candidatura.es_blanco:
                self.__resultados[candidatura.id_umv] = 0
                if categoria.posee_preferencias and candidatura.id_umv not in self.__preferencias[categoria.codigo]:
                    self.__preferencias[categoria.codigo][candidatura.id_umv] = 0
                if categoria.posee_tachas and candidatura.id_umv not in self.__tachas[categoria.codigo]:
                    self.__tachas[categoria.codigo][candidatura.id_umv] = 0
            
            # Sea cargo con tachas o preferencias, se inicializa la cantidad de preferencias
            # de cada candidato en 0.

            if not candidatura.es_blanco and categoria.posee_tachas:
                self.__detalle_tachas[categoria.codigo][candidatura.id_umv] = 0

            if not candidatura.es_blanco and categoria.posee_preferencias:
                self.__detalle_preferencias[categoria.codigo][candidatura.id_umv] = 0

    def validar_seleccion(self, seleccion):
        """Valida que la seleccion tiene una cantidad permitida de votos por
        categoria.

        Argumentos:
            seleccion -- un objeto de tipo seleccion
        """
        # a menos que digamos otra cosa la seleccion es valida
        selecciones_validas = True
        len_selec = 0
        categorias = Categoria.all()
        # voy a recorrer las categorias fijandome que la cantidad de votos
        # almacenados en el objeto seleccion es valida para cada una de ellas
        candidatos = seleccion.candidatos_elegidos()
        #agrego un contador para los candidatos de las cat con pref. o tachas
        cand_principal_preferencias_tachas = 0
        for categoria in categorias:
            len_selecciones_categoria = 0
            # sumo a la cantidad maxima de selecciones
            len_selec += int(categoria.max_selecciones)
            for candidato in candidatos:
                # si el candidato pertenece a la categoría sumo un voto para el
                # total de votos de la misma
                if candidato.cod_categoria == categoria.codigo:
                    len_selecciones_categoria += 1
            # si hay mas votos que la cantidad de selecciones maximas
            # permitidas salimos
            if len_selecciones_categoria > int(categoria.max_selecciones):
                selecciones_validas = False
                break

            if categoria.posee_preferencias or categoria.posee_tachas:
                cand_principal_preferencias_tachas += 1
                if categoria.posee_tachas:
                    tachas = seleccion.tachas_elegidas()
                    if len(tachas) > int(categoria.max_tachas):
                        selecciones_validas = False
                        break

                if categoria.posee_preferencias:
                    preferencias = seleccion.preferencias_elegidas(categoria.codigo)
                    if (len(preferencias) < int(categoria.min_preferencias) or
                        len(preferencias) > int(categoria.max_preferencias)):
                        selecciones_validas = False
                        break
        return selecciones_validas and len_selec == len(candidatos) + cand_principal_preferencias_tachas

    def sumar_seleccion(self, seleccion):
        """Suma una seleccion en caso de ser válida.

        Argumentos:
            seleccion -- Un objeto de tipo Seleccion.
        """
        if self.validar_seleccion(seleccion):
            # Si la seleccion es valida recorro cada candidatura y le sumo un
            # voto. Este es el lugar donde las cosas se hacen realidad.
            for categoria in Categoria.all():
                candidatos_elegidos = seleccion.candidato_categoria(categoria.codigo)
                if len(candidatos_elegidos)>0:
                    if not categoria.posee_preferencias and not categoria.posee_tachas:
                        candidato_principal = candidatos_elegidos[0]
                    else:
                        #si en las preferencias viene blanco
                        if candidatos_elegidos[0].es_blanco:
                            candidato_principal = candidatos_elegidos[0]
                        else:
                            candidato_principal = Candidatura.candidato_principal(categoria.codigo, candidatos_elegidos[0].cod_lista)

                    self._sumar_un_voto_candidato(candidato_principal.id_umv)

                    if categoria.posee_tachas and not candidato_principal.es_blanco:
                        incrementar_contador = True
                        for candidatura in seleccion.tachas_elegidas():
                            id_umv = candidatura.id_umv
                            if id_umv == -1:
                                id_umv = candidatura.principal.id_umv
                            nro_orden = candidatura.nro_orden
                            self.__detalle_tachas[id_umv][nro_orden] += 1

                            if incrementar_contador:
                                self.__tachas[id_umv] += 1
                                incrementar_contador = False

                    if categoria.posee_preferencias and not candidato_principal.es_blanco:
                        incrementar_contador = True
                        for preferencia in seleccion.preferencias_elegidas(categoria.codigo):
                            id_umv_preferencia = preferencia.id_umv
                            self.__detalle_preferencias[categoria.codigo][id_umv_preferencia] += 1

                            if incrementar_contador:
                                id_umv = candidato_principal.id_umv
                                self.__preferencias[categoria.codigo][id_umv] += 1
                                incrementar_contador = False
        else:
            raise ValueError("La cantidad de candidatos en la "
                             "seleccion no coincide con la esperada")
        
    def votos_candidato(self, id_umv):
        """Devuelve la cantidad de votos que tiene una candidatura.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
        """
        return self.__resultados[id_umv]

    def _sumar_valores(self, _dict):
        return sum([v for k, v in _dict.items()])

    def boletas_tachas(self, id_umv=None):
        if id_umv is not None:
            return self.__tachas[id_umv]
        else:
            return self.__tachas

    def boletas_preferencia(self, id_umv=None):
        candidato = Candidatura(id_umv=id_umv)
        if id_umv is not None:
            return self.__preferencias[candidato.cod_categoria][id_umv]
        else:
            return self.__preferencias

    def tachas_candidato(self, id_umv=None, nro_orden=None):
        if id_umv is not None and nro_orden is not None:
            return self.__detalle_tachas[id_umv][nro_orden]
        else:
            return self.__detalle_tachas

    def preferencias_candidato(self, cod_categoria, id_umv=None):
        if id_umv is not None:
            return self.__detalle_preferencias[cod_categoria][id_umv]
        else:
            return self.__detalle_preferencias[cod_categoria]
        
    def get_preferencias_agrupadas_por_principal(self, cod_categoria):
        """Obtiene los resultados de preferencias para una categoría específica agrupados por el candidato
        principal de cada lista.

        Args:
            cod_categoria (str): Código de la categoría de la cual se requiere obtener los resultados.

        Returns:
            OrderedDict: Resultados ordenados para la categoria.
        """
        
        agrupado = {}
        id_umv_principal_cod_lista_indexed = {c.cod_lista: c.id_umv for c in self.__candidatos_principales if c.cod_categoria == cod_categoria}
        for candidato in self.__candidaturas_seleccionables:
            if not candidato.es_blanco and candidato.cod_categoria == cod_categoria and candidato.categoria.posee_preferencias:
                
                id_umv_candidato_principal = id_umv_principal_cod_lista_indexed[candidato.cod_lista]

                if id_umv_candidato_principal not in agrupado:
                    agrupado[id_umv_candidato_principal] = {}
                agrupado[id_umv_candidato_principal][candidato.id_umv] = self.__detalle_preferencias[cod_categoria][candidato.id_umv]
        return agrupado

    def get_all_preferencias_agrupadas_por_principal(self):
        """Obtiene los resultados de preferencias de todas las categorías agrupando internamente por el candidato
        principal de cada lista.

        Args:
            cod_categoria (str): Código de la categoría de la cual se requiere obtener los resultados.

        Returns:
            OrderedDict: Resultados ordenados por caregoría según la posición definida.
        """

        categoria_sort_value_index = {categoria.codigo: categoria.posicion for categoria in Categoria.many(max_preferencias__gte=1)}
        
        agrupado = OrderedDict()
        id_umv_principal_cod_lista_indexed = {}

        for candidato_principal in self.__candidatos_principales:
            if candidato_principal.cod_categoria not in id_umv_principal_cod_lista_indexed:
                id_umv_principal_cod_lista_indexed[candidato_principal.cod_categoria] = {}
            id_umv_principal_cod_lista_indexed[candidato_principal.cod_categoria][candidato_principal.cod_lista] = candidato_principal.id_umv
        
        for candidato in self.__candidaturas_seleccionables:
            if not candidato.es_blanco and candidato.categoria.posee_preferencias:
                id_umv_candidato_principal = id_umv_principal_cod_lista_indexed[candidato.cod_categoria][candidato.cod_lista]
                
                if candidato.cod_categoria not in agrupado:
                    agrupado[candidato.cod_categoria] = {}
                
                if id_umv_candidato_principal not in agrupado[candidato.cod_categoria]:
                    agrupado[candidato.cod_categoria][id_umv_candidato_principal] = {}
                
                agrupado[candidato.cod_categoria][id_umv_candidato_principal][candidato.id_umv] = self.__detalle_preferencias[candidato.cod_categoria][candidato.id_umv]
        
        agrupado = dict(sorted(agrupado.items(), key=lambda x: categoria_sort_value_index[x[0]]))
        
        return agrupado
    
    def get_votos_actuales(self):
        """Devuelve la cantidad de votos que posee cada candidatura."""
        return self.__resultados

    def set_votos_candidato(self, id_umv, votos):
        """Devuelve la cantidad de votos que tiene una candidatura.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
            votos -- la cantidad de votos que se quiere establecer
        """
        assert type(votos) == int

        candidato = self.__candidaturas_seleccionables.one(id_umv=id_umv)
        if candidato is not None:
            self.__resultados[id_umv] = votos
        else:
            raise ValueError

    def set_tacha_candidato(self, id_umv, nro_orden, votos):
        """Devuelve la cantidad de votos que tiene una candidatura.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
            votos -- la cantidad de votos que se quiere establecer
        """
        assert type(votos) == int

        try:
            id_umv = int(id_umv)
            nro_orden = int(nro_orden)
        except:
            raise ValueError

        if id_umv is not None and id_umv in self.__detalle_tachas:
            self.__detalle_tachas[id_umv][nro_orden] = votos
        else:
            raise ValueError

    def set_preferencia_candidato(self, cod_categoria, id_umv, votos):
        """Devuelve la cantidad de votos que tiene una candidatura.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
            votos -- la cantidad de votos que se quiere establecer
        """
        assert type(votos) == int

        try:
            id_umv = int(id_umv)
        except:
            raise ValueError

        if id_umv is not None and id_umv in self.__detalle_preferencias[cod_categoria]:
            self.__detalle_preferencias[cod_categoria][id_umv] = votos
        else:
            raise ValueError

    def set_frecuencia_tachas_candidato(self, id_umv, cantidad):
        assert type(cantidad) == int

        try:
            id_umv = int(id_umv)
        except:
            raise ValueError

        if id_umv is not None and id_umv in self.__tachas:
            self.__tachas[id_umv] = cantidad
        else:
            raise ValueError

    def set_frecuencia_preferencias_candidato(self, id_umv, cantidad):
        assert type(cantidad) == int
        candidato = Candidatura(id_umv=id_umv)
        try:
            id_umv = int(id_umv)
        except:
            raise ValueError

        if id_umv is not None and id_umv in self.__preferencias:
            self.__preferencias[candidato.cod_categoria][id_umv] = cantidad
        else:
            raise ValueError

    def _sumar_un_voto_candidato(self, id_umv):
        """Le suma un voto a una candidatura.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
        """
        # aca es donde efectivamente se suman los votos.
        self.__resultados[id_umv] += 1

    def _sumar_votos_candidato(self, id_umv, votos):
        """ Le suma una determinada cantidad de votos a un candidato
            principal. Se usa única para regenerar el recuento desde_tag
            de forma mas eficiente.

        Argumentos:
            id_umv -- el id_umv de una candidatura.
        """
        # aca es donde efectivamente se suman los votos.
        self.__resultados[id_umv] += votos
