"""
Los asistentes se encargan de manejar el audio y la navegacion de las
diferentes "pantallas" del modulo Asistida.
"""
from gi.repository.GObject import timeout_add

from msa.constants import COD_LISTA_BLANCO
from msa.core.data import Speech
from msa.core.data.candidaturas import Categoria, Candidatura, Lista
from msa.modulos.sufragio.constants import (BOTON_LISTA_COMPLETA,
                                            BOTON_VOTAR_POR_CATEGORIAS)

from msa.core.logging import get_logger

logger = get_logger('asistentes')
class Asistente(object):

    """
    Los asistentes se encargan de manejar el audio y la navegacion de las
    diferentes "pantallas" del modulo Asistida.

    Asistente genérico de votación asistida, cada Asistente hereda de este.
    """

    indice_inicio = 1
    es_interactivo = True           # muestra teclado en pantalla

    def __init__(self, controlador, data, data_key=None, repetir=True):
        """
        Inicializa el asistente y empieza a enumerar las opciones.

        Args:
            controlador (Controlador): Es el controlador que esta usando esto. En general es una
                referencia al controlador de Asistida.
            data (dict): Los datos que se mandan a la vista.
            data_key (dict): La key en la que estan los datos concretos en elegir
                diccionario de datos
            repetir (bool): Indica si se debe repetir "inifinitamente" la locución.
        """
        self.opciones = []
        self.controlador = controlador
        self.controlador.ultima_tecla = None
        self.data = data
        self.data_key = data_key
        self.confirmando = None

        self.enumerar(repetir=repetir)

    def enumerar(self, error=None, repetir=True):
        """
        Enumera cada una de las opciones a elegir.

        Args:
            error (str): Agrega un mensaje de error al inicio de la locución.
            repetir (bool): indica si se debe repetir "inifinitamente" la locución.
        """
        textos = []
        if error is not None:
            textos.extend(error)
        preludio = self.get_preludio()
        if preludio is not None:
            textos.extend(preludio)
        self.opciones = self._get_opciones()
        for opcion in self.opciones:
            textos.extend(self._audio_opcion(opcion))
        epilogo = self.get_epilogo()
        if epilogo is not None:
            textos.extend(epilogo)
        self._decir(textos, repetir)

    def _decir(self, mensaje, repetir=True, cambio_estado=False):
        """
        Envía el mensaje al locutor.

        Args:
            mensaje  (str): Es el mensaje a emitir.
            repetir (bool): Hace que el locutor repita automáticamente el mensaje.
            cambio_estado (bool): Quien llama a este método pide que el timer de
            repetición de locución se reinicie, ya que hubo un nuevo tipo de mensaje
        """
        if cambio_estado:
            self.controlador.sesion.locutor.reset()
        self.controlador.sesion.locutor.decir(mensaje, repetir)

    def registrar_callback_fin_cola(self, callback):
        locutor = self.controlador.sesion.locutor
        locutor._audio_player.registrar_callback_fin_cola(callback)

    def _get_opciones(self):
        """
        Genera una lista con todas las opciones.

        Returns:
            list: Lista enumerada con las opciones.
        """
        opciones = list(enumerate(self.procesar_data(), self.indice_inicio))
        return opciones

    def _(self, key):
        """
        Shortcut para no poner Speech.one(key) en todos lados.

        Args:
            key (str): La key del objeto Speech.

        Returns:
            Speech: Audio con el texto recibido por parámetro.
        """
        return Speech.one(key).texto

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.

        Args:
            opcion (int): La opción a locutar.

        Returns:
            array.array: Arreglo con el mensaje armado según el parámetro
            recibido.
        """
        num_opcion, datos = opcion
        mensaje = [self._('para_votar'),
                   datos['texto_asistida'] if datos["codigo"] != "0"
                        else self._('agrupaciones_municipales'),
                   self._('presione'),
                   str(num_opcion)]
        return mensaje

    def procesar_data(self):
        """
        Procesa los datos del formato de voto y genera lo que necesito para
        asistida.

        Returns:
            array.array: Arreglo con la estructura de voto para asistida.

        """
        if self.data_key is not None:
            data = self.data[self.data_key]
        else:
            data = self.data

        blanco = None
        nueva_data = []
        for datum in data:
            if 'codigo' not in datum or \
                    not datum['codigo'].endswith(COD_LISTA_BLANCO):
                nueva_data.append(datum)
            else:
                blanco = datum

        if blanco is not None:
            nueva_data = nueva_data + [blanco]
            #self.indice_inicio = 0

        return nueva_data

    def get_preludio(self):
        """Lo que dice antes de la lista de opciones."""
        pass

    def get_epilogo(self):
        """Lo que dice después de la lista de opciones."""
        pass

    def elegir(self, numero):
        """Elige la opción que seleccionó el usuario.

        Args:
            numero (str): El número de opcion seleccionado.
        """
        opciones = dict(self.opciones)
        try:
            opcion = opciones.get(int(numero))
        except ValueError:
            opcion = None

        if opcion is None and not self.confirmando:
            self.opcion_invalida()
        else:
            self.callback(opcion, numero)

    def opcion_invalida(self):
        """
        Genera el texto en caso de que la opción elegida sea invalida y lo
        dice.
        """
        error = [self._("la_opcion"),
                 self._("que_ingreso"),
                 self._("no_existe")]
        self.enumerar(error=error)

    def cancelar(self):
        """
        Posibilita la cancelación de lo seleccionado.
        """
        self.confirmando = None
        self.controlador.cambiar_monitor()
        self.enumerar()

    def get_monitor(self):
        """
        Devuelve el texto que se utilizara en el indicador de estado abajo
        a la derecha del teclado. Esto ayuda a que la persona que esta
        asistiendo al elector pueda saber en que etapa del voto se encuentra
        el mismo sin comprometer el sectreto al voto.

        Returns:
            str: Cadena de caracteres vacía.
        """

        return ""

    def recordar(self):
        """Emite un recordatorio sonoro de interacción al usuario."""
        mensaje = [self._('no_olvide_apretar_numeral')]
        self._decir(mensaje, repetir=True)


class AsistenteModos(Asistente):

    """El asistente para la pantalla de seleccion de modos."""

    def get_monitor(self):
        """
        Devuelve el texto del monitor.

        Returns:
              list: Lista con el texto ``seleccionando_modo``
        """
        return _("seleccionando_modo")

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.
        Si se encuentra la setting "desactivar_lista_completa", se pasa al modo
        por categoría.

        Returns:
            array.array: Arreglo con los mensajes que se deberán mostrar.
        """
        if self.controlador.modulo.config("desactivar_lista_completa"):
            # si está presente esa setting, pasamos directamente al modo
            # por categoría
            self.controlador.send_command("seleccionar_modo", BOTON_VOTAR_POR_CATEGORIAS)
        else:
            mensaje = [
                self._('a_continuacion_usted'),
                self._('ingrese_nro_modo'),
                self._("confirmando_con_e_opcion"),
                self._("las_opciones_son")]
            return mensaje

    def procesar_data(self):
        """
        Procesa la data.

        Construye una lista para poder determinar si el modo de votación es
        basado en categorías o lista completa.

        Returns:
            list: Contiene el código (categorías o lista completa) y el texto de asistida.
        """
        modos = []
        for boton in self.controlador.modulo.config("botones_seleccion_modo"):
            if boton == BOTON_VOTAR_POR_CATEGORIAS:
                modos.append({'codigo': BOTON_VOTAR_POR_CATEGORIAS,
                              'texto_asistida': self._('categorias')})
            if boton == BOTON_LISTA_COMPLETA:
                modos.append({'codigo': BOTON_LISTA_COMPLETA,
                              'texto_asistida': self._('lista_completa')})

        return modos

    def _audio_opcion(self, opcion):
        """
        Genera el audio de la opción.

        Args:
            opcion (str): La opción a locutar.

        Returns:
             array.array: Arreglo con la opción y el texto de asistida correspondiente. Mensaje.
        """
        num_opcion, datos = opcion
        mensaje = [self._('para_votar_por'),
                   datos['texto_asistida'],
                   self._('presione'),
                   str(num_opcion)]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opción.

        Args:
            opcion (array.array):  la opcion elegida.
            numero (int): el número de opción que tiene la opción elegida.
        """
        self.controlador.send_command("seleccionar_modo", opcion['codigo'])


class AsistenteListaCompleta(Asistente):

    """Asistente para el modo de votacion por lista completa."""

    def get_monitor(self):
        """
        Devuelve el texto del monitor.

        Returns:
            list: Lista con el texto ``seleccionando_lista``.
        """
        return _("seleccionando_lista")

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Mensaje del preludio con los textos que
            deberan reproducirse.
        """
        mensaje = [
            self._('a_continuacion_usted'),
            self._('ingrese_nro_lista'),
            self._("confirmando_con_e_opcion"),
            self._("las_opciones_son")]
        return mensaje

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.

        Args:
            opcion (array.array): La opción a locutar.

        Returns:
            array.array: Arreglo con la construcción del mensaje que será interpretado
            por el locutor.
        """
        num_opcion, datos = opcion

        mensaje = [self._('para_votar'), self._('la_lista'), self._('numero'),
                   datos['texto_asistida']]

        if self.controlador.modulo.config("completa_dice_candidato"):
            lista = Lista.one(datos["codigo"])
            if lista is not None:
                for candidato in lista.candidatos:
                    if len(lista.candidatos) > 1:
                        mensaje.append(candidato.categoria.texto_asistida)
                    mensaje.append(candidato.texto_asistida)
            elif datos["codigo"] == "0":
                # casos especiales:
                mensaje.append(self._('agrupaciones_municipales'))

        mensaje += [self._('presione'),
                    str(num_opcion),
                    self._('pausa')
                    ]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.

        Args:
            opcion (array.array): La opcion elegida.
            numero (int): el número de opcion que tiene la opción elegida.
        """
        self.controlador.send_command("seleccionar_lista", opcion['codigo'])

    def procesar_data(self):
        """
        Procesa los datos del formato de voto y genera lo que se necesite para
        asistida.

        Returns:
            array.array: Formatea los datos en base a lo requerido por asistida.
        """
        if self.data_key is not None:
            data = self.data[self.data_key]
        else:
            data = self.data

        blanco = None
        nueva_data = []
        for datum in data:
            if 'codigo' not in datum or \
                    not datum['codigo'].endswith(COD_LISTA_BLANCO):
                nueva_data.append(datum)
            else:
                blanco = datum

        if blanco is not None:
            nueva_data = nueva_data + [blanco]

        return nueva_data


class AsistenteCargoListas(Asistente):
    """
    Asistente para el modo de votación por lista completa con listas
    sin gobernador u otros candidatos
    """
    def get_monitor(self):
        """
        Devuelve el texto del monitor.

        Returns:
              list: Lista con el texto ``seleccionando_cargo_lista``
        """
        return _("seleccionando_cargo_lista")

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        
        mensaje = [
            self._('a_continuacion_usted'),
            self._('ingrese_nro_cargo_lista'),
            self._("confirmando_con_e_opcion")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opción.

        Args:
            opcion (array.array): La opción elegida.
            numero (int): El número de opción elegida.
        """

        if "id_candidatura" in opcion:
            codigo = opcion['id_candidatura']
        elif opcion["codigo"] == "0":
            # casos especiales como "agrupaciones_municipales":
            codigo = None
        self.controlador.send_command("seleccionar_lista", codigo)

    def procesar_data(self):
        """
        Procesa los datos del formato de voto y genera lo que necesito para
        asistida.

        Returns:
            array.array: Arreglo con la estructura de voto para asistida.
        """
        if self.data_key is not None:
            data = self.data[self.data_key]
        else:
            data = self.data

        blanco = None
        nueva_data = []
        for datum in data:
            if 'codigo' not in datum or \
                    not datum['codigo'].endswith(COD_LISTA_BLANCO):
                nueva_data.append(datum)
            else:
                blanco = datum

        if blanco is not None:
            nueva_data += [blanco]

        return nueva_data


class AsistenteAdhesion(Asistente):

    """
       Asiste para seleccion de candidatos cuando hay adhesion segmentada.
    """

    def get_monitor(self):
        """
        Devuelve el texto del monitor.

        Returns:
              list: Lista con el texto ``seleccionando_candidatos``
        """
        ret = _("seleccionando_candidatos")
        return ret % self.categoria.nombre

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Arreglo con el mensaje. Contiene los textos que deberán
            reproducirse.
        """
        self.categoria = Categoria.one(self.data[1])
        mensaje = [
            self._("a_continuacion_usted"),
            self._("su_candidato_para"),
            self.categoria.texto_asistida,
            self._("confirmando_con_e_opcion")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.

        Args:
            opcion (array.array): La opción elegida.
            numero (int): Es el número de opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            categoria = Categoria.one(opcion['cod_categoria'])
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       self._("para"),
                       categoria.texto_asistida,
                       opcion['texto_asistida'],
                       self._("acuerdo_cancelar")]
            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            opcion_ = self.confirmando[0]
            self.controlador.seleccionar_lista([opcion_['codigo'],
                                               opcion_['cod_categoria'], None,
                                               False])


class AsistenteCandidatos(Asistente):

    """Asistente para votación por categorías."""

    def get_monitor(self):
        """
        Devuelve el texto del monitor.
        Para ello se basa en el atributo ``confirmado``

        Returns:
              list: Lista con el texto ``confirmando_candidatos`` si confirmado es True,
              sino, ``seleccionando_candidatos``
        """
        if self.confirmando:
            ret = _("confirmando_candidatos")
        else:
            ret = _("seleccionando_candidatos")

        return ret % self.categoria.nombre

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.

        Args:
            opcion (array.array): Es la opcion a locutar.
        """
        num_opcion, datos = opcion

        mensaje = [self._('para_votar')]

        if self.controlador.modulo.config("categoria_dice_lista_mas_candidato"):
            # si esta opción está activa, decimos el número y nombre de la lista
            # antes del nombre del candidato (útil para espejos)
            lista = Lista.one(datos["cod_lista"])
            if lista is not None:
                mensaje.append(datos['texto_asistida'])
                mensaje.append(self._('para'))
                mensaje.append(self._('la_lista'))
                mensaje.append(self._('numero'))
                mensaje.append(lista.texto_asistida)
            elif datos["codigo"] == "0":
                # casos especiales:
                mensaje.append(self._('agrupaciones_municipales'))
            else:
                mensaje.append(datos['texto_asistida'])

            mensaje += [self._('presione'),
                        str(num_opcion)]
        else:
            mensaje = [self._('para_votar'),
                       datos['texto_asistida'] if datos["codigo"] != "0"
                       else self._('agrupaciones_municipales'),
                       self._('presione'),
                       str(num_opcion)]

        return mensaje

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Mensaje con las opciones para seleccionar con la modalidad
            categorías.
        """
        self.categoria = Categoria.one(self.data["cod_categoria"])
        
        mensaje = [
            self._("a_continuacion_usted"),
            self._("su_candidato_para"),
            self.categoria.texto_asistida,
            self._("confirmando_con_e"),
            self._("las_opciones_son")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.

        En caso en que los datos no esten confirmados, se contruye el mensaje
        con la selección y el cargo .
        Si los datos no estan confirmados, el mensaje consta de los textos para
        comenzar la selección.

        Args:
            opcion (dict): la opción elegida.
            numero (int): Representa el número de opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            categoria = Categoria.one(opcion['cod_categoria'])
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       self._("para"),
                       categoria.texto_asistida]

            if self.controlador.modulo.config("categoria_dice_lista_mas_candidato"):
                # si tengo esta opción tengo que volver a decir el nombre de la lista y del candidato
                mensaje.append(opcion['texto_asistida'])
                lista = Lista.one(opcion["cod_lista"])
                if lista:
                    mensaje.append(self._('para'))
                    mensaje.append(self._('la_lista'))
                    mensaje.append(self._('numero'))
                    mensaje.append(lista.texto_asistida)
            else:
                mensaje.append(opcion['texto_asistida'])

            mensaje.append(self._("acuerdo_cancelar"))

            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            self.controlador.send_command("seleccionar_candidatos_asistida",
                    [self.confirmando[0]['cod_categoria'],
                    [self.confirmando[0]['id_umv']]])


class AsistenteCandidatoListas(Asistente):

    """Asistente para votacion por categorias."""

    def get_monitor(self):
        """Devuelve el texto del monitor."""
        if self.confirmando:
            ret = _("confirmando_listas")
        else:
            ret = _("seleccionando_listas_a_la") if self.categoria.codigo == 'CNJ' else _("seleccionando_listas_a")
        return ret % self.categoria.nombre

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.
        Argumentos:
            opcion -- la opcion a locutar.
        """
        num_opcion, datos = opcion

        mensaje = [self._('para_votar')]

        if datos['clase'] != 'Blanco':
            lista = Lista.one(datos["cod_lista"])
            # Si esta categoría es de lista abierta y todas las listas tienen una sola opcion, entonces tengo que decir 
            # el nombre del candidato junto con el nombre de la lista.
            categoria = Categoria.one(datos["cod_categoria"])
            if categoria.posee_preferencias:
                candidatos = Candidatura.many(cod_categoria=datos["cod_categoria"])
                sin_secundarios = True
                for cand in candidatos:
                    if len(cand.candidatos_secundarios) > 0:
                        sin_secundarios = False
                        break

                if sin_secundarios:
                    mensaje.append(datos["texto_asistida"])
                    mensaje.append(self._('para'))
                
            mensaje.append(self._('la_lista'))
            mensaje.append(self._('numero'))
            mensaje.append(lista.texto_asistida)
            
            if datos['cod_categoria'] == "PVC":
                mensaje.append(self._("presidente"))
                mensaje.append(lista.datos_extra["presidente"])
                mensaje.append(self._("vice_1"))
                mensaje.append(lista.datos_extra["vice_1"])
                mensaje.append(self._("vice_2"))
                mensaje.append(lista.datos_extra["vice_2"])
            
            
        else:
            mensaje.append(datos["texto_asistida"])

        mensaje += [self._('presione'),
                    str(num_opcion),
                    self._('pausa')]

        return mensaje

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        self.categoria = Categoria.one(self.data["cod_categoria"])
        mensaje = [
            self._("a_continuacion_usted"),
            self._("su_lista_candidatos_a_la") if self.categoria.codigo == 'CNJ' else self._("su_lista_candidatos_a"),
            self.categoria.texto_asistida,
            self._("confirmando_con_e_opcion"),
            self._("las_opciones_son")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.
        Argumentos:
            opcion -- la opcion elegida.
            numero -- el numero de opcion que tiene la opcion elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            categoria = Categoria.one(opcion['cod_categoria'])
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       self._("para"),
                       categoria.texto_asistida]

            if opcion['codigo'] != COD_LISTA_BLANCO:
                lista = Lista.one(opcion["cod_lista"])
                mensaje.append(self._('para'))
                mensaje.append(self._('la_lista'))
                mensaje.append(self._('numero'))
                mensaje.append(lista.texto_asistida)
                
                if opcion['cod_categoria'] == "PVC":
                    mensaje.append(self._("presidente"))
                    mensaje.append(lista.datos_extra["presidente"])
                    mensaje.append(self._("vice_1"))
                    mensaje.append(lista.datos_extra["vice_1"])
                    mensaje.append(self._("vice_2"))
                    mensaje.append(lista.datos_extra["vice_2"])
                
                if categoria.posee_preferencias:
                    candidatos = Candidatura.many(cod_categoria=opcion["cod_categoria"])
                    sin_secundarios = True
                    for cand in candidatos:
                        if len(cand.candidatos_secundarios) > 0:
                            sin_secundarios = False
                            break

                    if sin_secundarios:                                        
                        mensaje.append(self._("el_candidato"))
                        mensaje.append(opcion["texto_asistida"])
                
            else:
                mensaje.append(opcion['texto_asistida'])

            mensaje.append(self._("acuerdo_cancelar"))

            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            self.controlador.send_command("seleccionar_candidatos_asistida",
                    [self.confirmando[0]['cod_categoria'],
                    [self.confirmando[0]['id_umv']]])


class AsistentePreferenciasCandidato(Asistente):

    """Asistente para votacion por categorias."""
    
    elegidos = None

    def get_monitor(self):
        """Devuelve el texto del monitor."""
        if self.confirmando:            
            ret = _("confirmando_preferentes")
        else:
            ret = _("seleccionando_preferentes")            

        return ret % self.categoria.nombre

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.
        Argumentos:
            opcion -- la opcion a locutar.
        """
        num_opcion, datos = opcion

        mensaje = [self._('para_votar')]

        if datos['clase'] != 'Blanco':
            mensaje.append(self._('el_candidato'))
            mensaje.append(self._('con_numero_de_orden'))
            mensaje.append(str(datos['nro_orden']))
            mensaje.append(datos['texto_asistida'])
            mensaje.append(self._('presione'))
            mensaje.append(str(num_opcion))
            mensaje.append(self._('pausa'))
        else:
            mensaje.append(datos["texto_asistida"])
            mensaje += [self._('presione'),
                        str(num_opcion),
                        self._('pausa')]

        return mensaje

    def _get_opciones(self):
        """Genera una lista con todas las opciones que no fueron elegidas."""
        opciones = list(enumerate(self.procesar_data(), self.indice_inicio))
        if self.elegidos is None:
            return opciones
        else:
            elegidos = [cand[0]["id_umv"] for cand in self.elegidos]
            #dejo el mismo orden inicial sacando los que ya selecciono
            opciones_no_elegidas = [opcion for opcion in opciones
                                    if opcion[1]["id_umv"] not in elegidos]
            return opciones_no_elegidas

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        self.categoria = Categoria.one(self.data["cod_categoria"])
        if self.categoria.max_preferencias>1:
            if self.elegidos is not None:
                nro_candidato = len(self.elegidos) + 1
                permite_saltear = (len(self.elegidos) >= self.categoria.min_preferencias
                                    and len(self.elegidos) < self.categoria.max_preferencias)
            else:
                nro_candidato = 1
                permite_saltear = False
            mensaje = [
            self._("a_continuacion_usted"),
            self._("su_candidato_nro"),
            str(nro_candidato),
            self._("para"),
            self.categoria.texto_asistida if self.categoria.codigo != 'PVC' else self._('cargo_conduccion_nacional'),
            self._('confirmando_con_e')]
            if permite_saltear:
                mensaje.append(self._('saltear_preferencias'))
            mensaje.append(self._("las_opciones_son"))
        else:
            mensaje = [
            self._("a_continuacion_usted"),
            self._('su_candidato_preferente_para'),
            self.categoria.texto_asistida if self.categoria.codigo != 'PVC' else self._('cargo_conduccion_nacional'),
            self._('confirmando_con_e'),
            self._("las_opciones_son")]
        return mensaje

    def elegir(self, numero):
        """Elige la opcion que seleccionó el usuario.

        Argumentos:
            numero -- El numero de opcion seleccionado.
        """
        opciones = dict(self.opciones)
        try:
            opcion = opciones.get(int(numero))
        except ValueError:
            opcion = None

        #si es una cantidad valida dejo pasar el opcion None para no obligarlo
        #que llegue a max_preferencias
        if opcion is None and not self.confirmando and not self.cantidad_valida():
            self.opcion_invalida()
        else:
            self.callback(opcion, numero)

    def cantidad_valida(self):
        if self.elegidos is None:
            return False
        return (len(self.elegidos) >= self.categoria.min_preferencias
                and len(self.elegidos) <= self.categoria.max_preferencias)

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.
        Argumentos:
            opcion -- la opcion elegida.
            numero -- el numero de opcion que tiene la opcion elegida.
        """
        if opcion is not None:
            if self.elegidos is None:
                self.elegidos = []
            self.elegidos.append([opcion, numero])

        #si llego a la cantidad de candidatos maxima o apreto numeral estando entre
        #un rango de candidatos validos mostramos el mensaje para que confirme
        len_elegidos = 0 if self.elegidos is None else len(self.elegidos)

        if self.confirmando is None:
            if (len_elegidos == self.categoria.max_preferencias
                or (len_elegidos >= self.categoria.min_preferencias and opcion is None)
            ):
                mensaje = [self._("ud_eligio")]
                self.confirmando = self.elegidos
                for seleccion in self.elegidos:
                    opcion = seleccion[0]
                    numero = seleccion[1]
                    mensaje.extend([self._("la_opcion"),
                            self._("numero"),
                            numero,
                            opcion['texto_asistida']])

                lista = Lista.one(codigo=opcion['cod_lista'])
                mensaje.append(self._("como_candidato_preferente_para"))
                mensaje.append(self.categoria.texto_asistida if self.categoria.codigo != 'PVC' else self._('cargo_conduccion_nacional'))
                mensaje.append(self._('para'))
                mensaje.append(self._('la_lista'))
                mensaje.append(self._('numero'))
                mensaje.append(lista.texto_asistida)

                mensaje.append(self._("acuerdo_cancelar"))

                self._decir(mensaje)
                self.controlador.cambiar_monitor()
            else:
                self.enumerar(repetir=True)
        else:            
            candidatos = [seleccion[0]['id_umv'] for seleccion in self.confirmando]            
            self.controlador.send_command("seleccionar_preferente_asistida", [
                self.categoria.codigo, candidatos])

    def cancelar(self):
        self.elegidos = None
        self.confirmando = None
        self.controlador.cambiar_monitor()
        self.enumerar()


class AsistenteConsultaPopular(Asistente):

    """Asitente para eleccion de consulta popular."""

    def get_monitor(self):
        """
        Devuelve el texto del monitor.
        Para ello se basa en el atributo ``confirmado``

        Returns:
              list: Lista con el texto ``confirmando_candidatos`` si confirmado es True,
              sino, ``seleccionando_candidatos``
        """
        if self.confirmando:
            ret = _("confirmando_candidatos")
        else:
            ret = _("seleccionando_candidatos")

        return ret % self.categoria.nombre

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Arreglo que representa el mensaje que deberá reproducirse.
            El mismo consta de las opciones de consulta popular disponibles.
        """
        self.categoria = Categoria.one(self.data["cod_categoria"])
        mensaje = [
            self._("a_continuacion_usted"),
            self._("la_opcion"),
            self._("para"),
            self.categoria.texto_asistida,
            self._("confirmando_con_e_opcion"),
            self._("las_opciones_son")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opción.
        En el caso de que sea una confirmación, se envía la orden al
        controlador para que procesada con la pantalla de "selección de candidatos",
        en caso contrario se construye el mensaje que indica la selección de candidato.

        Args:
            opcion (dict): La opción elegida.
            numero (int): Es el número de opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            categoria = Categoria.one(opcion['cod_categoria'])
            mensaje = [self._("ud_eligio"),
                       numero,
                       self._("para"),
                       categoria.texto_asistida,
                       opcion['texto_asistida'],
                       self._("acuerdo_cancelar")]
            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            self.controlador.send_command("seleccionar_candidatos_asistida",
                [self.confirmando[0]['cod_categoria'],
                 [self.confirmando[0]['id_umv']]])


class AsistentePartido(Asistente):

    """Asistente para seleccion de partido."""

    def __init__(self, controlador, data, data_key=None, repetir=True):
        blanco = Candidatura.first(clase="Blanco").to_dict()
        data.append(blanco)
        Asistente.__init__(self, controlador, data, data_key, repetir)

    def get_monitor(self):
        """
        Devuelve el texto del monitor.
        Para ello se basa en el atributo ``confirmado``

        Returns:
              list: Lista con el texto ``confirmando_partido`` si confirmado es True,
              sino, ``seleccionando_partido``
        """
        if self.confirmando:
            ret = _("confirmando_partido")
        else:
            ret = _("seleccionando_partido")

        return ret

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        mensaje = [
            self._("a_continuacion_usted"),
            self._("ingrese_nro_interna")]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opción.

        Args:
            opcion (dict): La opción elegida.
            numero (int): El número con la opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       opcion['texto_asistida'],
                       self._("acuerdo_cancelar")]
            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            if self.confirmando[0]['codigo'] == COD_LISTA_BLANCO:
                self.controlador.send_command("seleccionar_lista",
                                              self.confirmando[0]['codigo'])
            else:
                self.controlador.send_command("seleccionar_partido_asistida",
                                         [self.confirmando[0]['codigo'],
                                          None])


class AsistentePartidosCat(Asistente):

    """Asistente para seleccion de partido."""

    def __init__(self, controlador, data, data_key=None, repetir=True):
        categoria = data[0]['cod_categoria']
        blanco = Candidatura.one(clase="Blanco",
                                 cod_categoria=categoria).to_dict()
        data.append(blanco)
        Asistente.__init__(self, controlador, data, data_key, repetir)

    def procesar_data(self):
        """Procesa los datos del formato de voto y genera lo que necesito para
        asistida.

        Returns:
              array.array: Arreglo con la estructura requerida por el
              Asistente de Partidos por cartegorías.
        """
        if self.data_key is not None:
            data = self.data[self.data_key]
        else:
            data = self.data

        return data

    def get_monitor(self):
        """
        Devuelve el texto del monitor.
        Para ello se basa en el atributo ``confirmado``

        Returns:
              list: Lista con el texto ``confirmando_partido`` si confirmado es True,
              sino, ``seleccionando_partido``
        """
        if self.confirmando:
            ret = _("confirmando_partido")
        else:
            ret = _("seleccionando_partido")

        return ret

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        self.categoria = Categoria.one(self.data[0]['cod_categoria'])
        mensaje = [
                self._('a_continuacion_usted'),
                self._("ingrese_nro_interna"),
                self._("para"),
                self.categoria.texto_asistida]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opción.

        Args:
            opcion (dict): La opción elegida.
            numero (int): el número de opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       opcion['texto_asistida'],
                       self._("acuerdo_cancelar")]
            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            if self.confirmando[0]['codigo'] == COD_LISTA_BLANCO:
                self.controlador.send_command("seleccionar_candidatos_asistida",
                    [self.confirmando[0]['cod_categoria'],
                    [self.confirmando[0]['id_umv']]])
            else:
                self.controlador.send_command(
                    "seleccionar_partido_asistida",
                    [self.confirmando[0]['codigo'],
                    self.confirmando[0]['cod_categoria']])


class AsistenteConfirmacion(Asistente):

    """Asistente para confirmacion de voto."""

    def __init__(self, controlador, data, data_key=None, repetir=True):
        if (len(data) == 1 and not
                controlador.modulo.config("confirmar_unico_cargo")):
            self.controlador = controlador
            self.elegir(None)
            self.es_interactivo = False     # no mostrar teclado (controlador)
        else:
            Asistente.__init__(self, controlador, data, data_key, repetir)

    def get_monitor(self):
        """
        Devuelve el texto del monitor.

        Returns:
              list: Lista con el texto ``confirmando``
        """
        return _("confirmando")

    def get_preludio(self):
        """Devuelve el mensaje del preludio."""
        mensaje = [self._("ud_confirmo")]

        return mensaje

    def get_epilogo(self):
        """
        Lo que dice después de la lista de opciones.

        Returns:
            array.array: Arreglo con los mensajes de confirmación.
        """
        mensaje = [self._('confirmar_ud_confirmo_fin'),
                   self._('confirmar_ud_confirmo_fin2')]

        return mensaje

    def _audio_opcion(self, opcion):
        """
        Genera el audio de la opción recibida como parámetro.

        Args:
            opcion (array.array): Contiene la selección realizada por el
                usuario.
        Returns:
            array.array: Arreglo con los textos que conforman el mensaje reproducible.
        """
        num_opcion, datos = opcion
        categoria = Categoria.one(datos['categoria']['codigo'])
        lista = Lista.one(datos['candidatos'][0]['cod_lista'])
        es_consulta_popular = datos['categoria']['consulta_popular']

        # Tipo de entidad: 'candidato' u 'opción' (para consulta popular).
        if es_consulta_popular:
            tipo_entidad = self._('la_opcion')
        else:
            if len(datos['candidatos'])>1:
                tipo_entidad = self._('los_candidatos')
            else:
                tipo_entidad = self._('el_candidato')

        mensaje = [
            self._('para'),
            Categoria.one(datos['categoria']['codigo']).texto_asistida,
            tipo_entidad]

        for candidato in datos['candidatos']:
            if categoria.posee_preferencias:
                    mensaje.append(self._('con_numero_de_orden'))
                    mensaje.append(str(candidato['nro_orden']))
            
            mensaje.append(candidato['texto_asistida'])


        # Si corresponde, agrega número y nombre de la lista al mensaje.
        if lista and not es_consulta_popular:
            mensaje += [
                self._('para'),
                self._('la_lista'),
                self._('numero'),
                lista.texto_asistida]
        return mensaje

    def elegir(self, data):
        """Confirma la elección, no utiliza número de opcion (data)"""
        # ocultar inmediatamente el teclado:
        self.controlador.send_command("ocultar_teclado")
        def _interfaz():
            self.controlador.send_command("agradecimiento")

        def _inner():
            self.controlador.prepara_impresion()
            self._decir([self._("imprimiendo")], False)
            self.controlador.confirmar_seleccion(data)

        timeout_add(1000, _interfaz)
        timeout_add(2000, _inner)

    def cancelar(self):
        """
        Cancela una opción.

        Los pasos que requerisos son:
            * Apagar el locutor.
            * Cambiar de estado el módulo.
            * Comenzar nuevamente desde la pantalla de inicio.
        """
        self.controlador.sesion.locutor.shutup()
        self.controlador.modulo.set_estado(None)
        self.controlador.modulo._comenzar()


class AsistenteVerificacion(AsistenteConfirmacion):

    """Asistente para verificacion de votos ya generados."""

    def __init__(self, controlador, data, data_key=None, repetir=True):
        Asistente.__init__(self, controlador, data, data_key, repetir)

    def get_epilogo(self):
        """Lo que dice después de la lista de opciones."""
        pass

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Devuelve el mensaje según ``ud_voto``.
        """
        mensaje = [self._("ud_voto")]

        return mensaje

    def _decir(self, mensaje, repetir=True, cambio_estado=False):
        """
        Envía el mensaje al locutor.

        Args:
            mensaje (array.array): El mensaje a emitir
            repetir (bool): Hace que el locutor repita automáticamente el mensaje
            cambio_estado (bool): Quien llama a este método pide que el timer de
                repetición de locución se reinicie, ya que hubo un nuevo tipo
                de mensaje
        """
        def _inner():
            rampa = self.controlador.modulo.rampa
            self.controlador.modulo.pantalla_insercion()
            rampa.expulsar_boleta()

        self.registrar_callback_fin_cola(_inner)
        AsistenteConfirmacion._decir(self, mensaje, repetir, cambio_estado)


class AsistenteCandidatosParaguay(AsistenteCandidatos):

    def _audio_opcion(self, opcion):
        """
        Genera el contenido del texto del audio de la opción.

        Args:
            opcion (array.array): Es la opcion a locutar.
        """
        num_opcion, datos = opcion

        mensaje = [self._('para_votar')]

        if self.controlador.modulo.config("categoria_dice_lista_mas_candidato"):
            # si esta opción está activa, decimos el número y nombre de la lista
            # antes del nombre del candidato (útil para espejos)
            lista = Lista.one(datos["cod_lista"])
            if lista is not None:
                if self.controlador.categoria_con_presidente_vice(datos):
                    mensaje.append(self._("presidente"))                
                mensaje.append(datos['texto_asistida'])
                if self.controlador.categoria_con_presidente_vice(datos):
                    mensaje.append(self._("vice_1"))
                    mensaje.append(datos["secundarios_datos_extra"][0]["nombre"])
                    mensaje.append(self._("vice_2"))
                    mensaje.append(datos["secundarios_datos_extra"][1]["nombre"])
                mensaje.append(self._('para'))
                mensaje.append(self._('la_lista'))
                mensaje.append(self._('numero'))
                mensaje.append(lista.texto_asistida)
            elif datos["codigo"] == "0":
                # casos especiales:
                mensaje.append(self._('agrupaciones_municipales'))
            else:
                mensaje.append(datos['texto_asistida'])

            mensaje += [self._('presione'),
                        str(num_opcion),
                        self._('pausa')]
        else:
            mensaje = [self._('para_votar'),
                       datos['texto_asistida'] if datos["codigo"] != "0"
                       else self._('agrupaciones_municipales'),
                       self._('presione'),
                       str(num_opcion),
                       self._('pausa')
                       ]
        return mensaje

    def callback(self, opcion, numero):
        """
        Callback que se ejecuta cuando se selecciona una opcion.

        En caso en que los datos no esten confirmados, se contruye el mensaje
        con la selección y el cargo .
        Si los datos no estan confirmados, el mensaje consta de los textos para
        comenzar la selección.

        Args:
            opcion (dict): la opción elegida.
            numero (int): Representa el número de opción elegida.
        """
        if self.confirmando is None:
            self.confirmando = [opcion, numero]
            categoria = Categoria.one(opcion['cod_categoria'])
            mensaje = [self._("ud_eligio_opcion"),
                       numero,
                       self._("para"),
                       categoria.texto_asistida]

            if self.controlador.modulo.config("categoria_dice_lista_mas_candidato"):
                # si tengo esta opción tengo que volver a decir el nombre de la lista y del candidato
                if self.controlador.categoria_con_presidente_vice(opcion):
                    mensaje.append(self._("presidente"))                
                mensaje.append(opcion['texto_asistida'])
                if self.controlador.categoria_con_presidente_vice(opcion):
                    mensaje.append(self._("vice_1"))
                    mensaje.append(opcion["secundarios_datos_extra"][0]["nombre"])
                    mensaje.append(self._("vice_2"))
                    mensaje.append(opcion["secundarios_datos_extra"][1]["nombre"])
                lista = Lista.one(opcion["cod_lista"])
                if lista:
                    mensaje.append(self._('para'))
                    mensaje.append(self._('la_lista'))
                    mensaje.append(self._('numero'))
                    mensaje.append(lista.texto_asistida)
            else:
                mensaje.append(opcion['texto_asistida'])

            mensaje.append(self._("acuerdo_cancelar"))

            self._decir(mensaje)
            self.controlador.cambiar_monitor()
        else:
            self.controlador.send_command("seleccionar_candidatos_asistida",
                    [self.confirmando[0]['cod_categoria'],
                    [self.confirmando[0]['id_umv']]])

class AsistenteConsultaPopularParaguay(AsistenteConsultaPopular):

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Arreglo que representa el mensaje que deberá reproducirse.
            El mismo consta de las opciones de consulta popular disponibles.
        """
        self.categoria = Categoria.one(self.data["cod_categoria"])
        mensaje = [
            self._("a_continuacion_usted"),
            self._("su_candidato_para"),
            self.categoria.texto_asistida,
            self._("confirmando_con_e_opcion"),
            self._("las_opciones_son")]
        return mensaje

class AsistenteConfirmacionParaguay(AsistenteConfirmacion):

    def _audio_opcion(self, opcion):
        """
        Genera el audio de la opción recibida como parámetro.

        Args:
            opcion (array.array): Contiene la selección realizada por el
                usuario.
        Returns:
            array.array: Arreglo con los textos que conforman el mensaje reproducible.
        """
        num_opcion, datos = opcion
        categoria = Categoria.one(datos['categoria']['codigo'])
        lista = Lista.one(datos['candidatos'][0]['cod_lista'])
        # Esto es para que diga el número y nombre de la lista en
        # confirmación
        try:
            if datos['categoria'].get('max_preferencias', 0) < 1:
                datos_pv = {
                            'secundarios_datos_extra': datos['candidatos'][0].get('secundarios_datos_extra',[]),
                            'cargo_ejecutivo': datos['categoria']['cargo_ejecutivo'],
                            'codigo': datos['candidatos'][0]['codigo']
                            }
                dice_presi_vice = self.controlador.categoria_con_presidente_vice(datos_pv)
            else:
                dice_presi_vice = False
        except Exception:
            dice_presi_vice = False

        if lista:
            mensaje = [
                self._('para'),
                categoria.texto_asistida]

            if dice_presi_vice or categoria.codigo == 'PVC' or len(datos['candidatos'])>1:
                mensaje.append(self._('los_candidatos'))
            else:
                mensaje.append(self._('el_candidato'))

            mensaje.extend([
                self._('de'),
                self._('la_lista'),
                self._('numero'),
                lista.texto_asistida
            ])

            for candidato in datos['candidatos']:
                if categoria.codigo == 'PVC':
                    mensaje.append(self._("presidente"))
                    mensaje.append(lista.datos_extra["presidente"])
                    mensaje.append(self._("vice_1"))
                    mensaje.append(lista.datos_extra["vice_1"])
                    mensaje.append(self._("vice_2"))
                    mensaje.append(lista.datos_extra["vice_2"])
                    mensaje.append(self._('y_candidato_a'))
                    mensaje.append(self._('cargo_conduccion_nacional'))

                if categoria.posee_preferencias:
                    mensaje.append(self._('con_numero_de_orden'))
                    mensaje.append(str(candidato['nro_orden']))

                if dice_presi_vice:
                    mensaje.append(self._("presidente"))

                mensaje.append(candidato['texto_asistida'])

                if dice_presi_vice:
                    mensaje.append(self._("vice_1"))
                    mensaje.append(candidato["secundarios_datos_extra"][0]["nombre"])
                    mensaje.append(self._("vice_2"))
                    mensaje.append(candidato["secundarios_datos_extra"][1]["nombre"])
        else:
            # BLC
            mensaje = [
                self._('para'),
                categoria.texto_asistida,
                self._('la_opcion'),
                datos['candidatos'][0]['texto_asistida']]
        mensaje.extend([self._('pausa')])
        return mensaje


class AsistenteVerificacionParaguay(AsistenteConfirmacionParaguay):

    """Asistente para verificacion de votos ya generados."""

    def __init__(self, controlador, data, data_key=None, repetir=True):
        Asistente.__init__(self, controlador, data, data_key, repetir)

    def get_epilogo(self):
        """Lo que dice después de la lista de opciones."""
        pass

    def get_preludio(self):
        """
        Devuelve el mensaje del preludio.

        Returns:
            array.array: Devuelve el mensaje según ``ud_voto``.
        """
        mensaje = [self._("ud_voto")]

        return mensaje

    def _decir(self, mensaje, repetir=True, cambio_estado=False):
        """
        Envía el mensaje al locutor.

        Args:
            mensaje (array.array): El mensaje a emitir
            repetir (bool): Hace que el locutor repita automáticamente el mensaje
            cambio_estado (bool): Quien llama a este método pide que el timer de
                repetición de locución se reinicie, ya que hubo un nuevo tipo
                de mensaje
        """
        def _inner():
            rampa = self.controlador.modulo.rampa
            self.controlador.modulo.pantalla_insercion()
            rampa.expulsar_boleta()

        self.registrar_callback_fin_cola(_inner)
        AsistenteConfirmacionParaguay._decir(self, mensaje, repetir, cambio_estado)