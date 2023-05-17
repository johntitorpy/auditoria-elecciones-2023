"""
Modulo base de las rampas.

maneja la interaccion entre la impresora y el lector y el usuario.
"""
from gi.repository.GObject import idle_add
import time
from gi.repository.GLib import timeout_add, source_remove

from msa.core.armve.constants import DEV_PRINTER
from msa.core.exceptions import MesaNoEncontrada
from msa.core.rfid.constants import (NO_TAG, TAG_ADMIN, TAG_APERTURA, TAG_COLISION,
                                     TAG_PRESIDENTE_MESA, TAG_RECUENTO,
                                     TAG_USUARIO_MSA, TAG_VACIO, TAG_VOTO)
from msa.modulos import get_sesion
from msa.modulos.base.decorators import semaforo, si_tiene_conexion, presencia_on_required
from msa.modulos.constants import (E_CARGA, E_CONFIRMACION, E_INICIAL,
                                   E_REGISTRANDO, E_SETUP, E_VOTANDO,
                                   SUBMODULO_DATOS_ESCRUTINIO)


class RampaBase(object):

    """Rampa generica. Se encarga de manejar los estados de papel en la impresora y el
    estado de los chips.

    Attributes:
        modulo (modulos.base.modulo.ModuloBase): modulo con el que se asocia.
        sesion (modulos.Sesion): la sesion actual
        _servicio (core.ipc.client.IPCClient): cliente IPC.
        tiene_conexion (bool): estado de coneccion al cliente IPC.
        _timeout_autofeed (int): valor de retorno de :func:`GLib.timeout_add`. Es el ID del evento que se ejecuta.
        tiene_papel (bool):
            True si hay un papel en la rampa.
        tag_leido (list[bytes]): datos del tag leído.


    """

    def __init__(self, modulo):
        """


        Arguments:
            modulo (str): referencia al modulo que maneja la rampa.
        """
        self.modulo = modulo
        self.sesion = get_sesion()

        self._servicio = self.sesion._servicio
        self.tiene_conexion = self._servicio is not None
        self._timeout_autofeed = None

        if self.tiene_conexion:
            # reseteamos el RFID por precaución cada vez que arrancamos una
            # rampa nueva
            self.sesion.logger.debug("Iniciando rampa...")
            self.reset_rfid()
            # ojo que esto no verifica correctamente que tenga papel, no puedo
            # saber si está viendo el sensor solamente o ademas el papel esta
            # tomado, pero este conocimiento es mejor que nada.
            self.tiene_papel = self._servicio.tiene_papel
            self.tag_leido = self._servicio.get_tag()
        else:
            self.tiene_papel = False
            self.tag_leido = None

        self.desregistrar_eventos()
        self.registrar_eventos()


    def maestro(self):
        pass

    def cambio_sensor_1(self, data):
        """Callback que se corre cuando el sensor 1 se dispara.

        El estado que nos interesa es el que manda False en el sensor_1
        ya que nos dice que el papel ya esta listo para leer el chip.
        """
        sensor_1 = data['sensor_1']

        if not sensor_1:
            self.tiene_papel = False
            self.maestro()

    def cambio_sensor_2(self, data):
        """
        Callback que se corre cuando se recibe el evento de autofeed_end.

        El estado que nos interesa es el sensor_2 en 0 ya que nos dice
        que el papel ya esta listo para leer el chip
        """
        sensor_1 = data['sensor_1']
        sensor_2 = data['sensor_2']
        sensor_3 = data['sensor_3']

        if not sensor_2 and sensor_1:
            self.tiene_papel = True
            self.maestro()
            # luego del autofeed, el sensor 3 se desactiva, notificar:
            self.cambio_sensor_3(data)

    def cambio_sensor_3(self, data):
        """
        Callback que se corre cuando se recibe el evento de rampa.

        Se verifica que el papel sea insertado correctamente (3er sensor en estado correcto = 0). En ese caso (solo si
        está votando), lanza un chequeo en segundo plano a los 1.5 segundos.

        Si el 3er sensor no pasa al estado correcto, pide al modulo que muestre un dialogo de advertencia y expulsa.
        Esto evita que siga votando y luego le de el error al grabar.

        .. function:: cambio_sensor_3._verificar_autofeed()

            Es la funcion que corre en segundo plano con :func:`GLib.timeout_add` en caso que la boleta haya sido
            insertada de forma incorrecta.

        """
        sensor_1 = data['sensor_1']
        sensor_2 = data['sensor_2']
        sensor_3 = data['sensor_3']

        self.sesion.logger.debug("Evento Sensor Rampa: %s", data)
        if self._timeout_autofeed is not None:
            # limpio el timeout por si el sensor pasó al estado correcto
            # (secuencia normal mientras va ingresando el papel)
            # o los otros sensores cambiaron de estado (i.e. se quitó el papel)
            source_remove(self._timeout_autofeed)
            self._timeout_autofeed = None
            self.sesion.logger.debug("Levantando timeout autofeed...")
        if sensor_3 and not sensor_2 and sensor_1:
            # se ingresó mal la boleta? (el tercer sensor debería ser 0)
            def _verificar_autofeed():
                self.sesion.logger.warning("Timeout autofeed estado papel!")
                ok = self.get_papel_listo()
                if self.modulo.estado != E_VOTANDO:
                    # ya está imprimiendo o retiró el papel...
                    self.sesion.logger.debug("No verif. estado papel")
                elif not ok:
                    # no se hizo el autofeed completo, volver a inicio:
                    self.tiene_papel = False
                    self.maestro()
                    self.modulo.show_dialogo("papel_no_insertado_ok")
                    self.sesion.logger.debug("Papel no posicionado ok")
                    # reinicio preventivo de la impresora
                    self.reset_printer()
                    self.expulsar_boleta("autofeed")
                    timeout_add(4000, self.modulo.hide_dialogo)
                else:
                    self.sesion.logger.debug("Papel Verificado ok")
                self._timeout_autofeed = None
            # esperar para actualizar UI y darle tiempo a los sensores:
            self.sesion.logger.debug("Estableciendo timeout autofeed")
            self._timeout_autofeed = timeout_add(1500, _verificar_autofeed)

    def _cambio_tag(self, tipo_lectura, tag=None):
        """
        Callback de cambio de tag.

        .. Warning::
            Si es valido retorna :meth:`cambio_tag(tipo_lectura, tag) <cambio_tag>` y sino no retorna nada.
            Deberia retornar siempre algo o nunca retornar. Además, :meth:`cambio_tag <cambio_tag>`
            es un método sin valor de retorno.

        .. todo::
            Arreglar retorno condicional

        Arguments:
            tipo_lectura (str): el tipo de lectura. Debe ser alguno de los :ref:`core.rfid.constants.tipo_tags`.
            tag (core.documentos.soporte_digital.SoporteDigital): una instancia de ``SoporteDigital``.
        """
        valido = True

        if tag is not None and tag.tipo in (TAG_PRESIDENTE_MESA,
                                            TAG_USUARIO_MSA):
            valido = tag.verificar_firma_credencial()

        if valido:
            return self.cambio_tag(tipo_lectura, tag)
        else:
            self.sesion.logger.info("Falló la verificación de la firma.")

    def cambio_tag(self, tipo_lectura, tag):
        """Cuando el TAG leído es válido verifica que tipo de lectura es:

        1. core.rfid.constants.TAG_COLISION: llama a :meth:`tag_colision <tag_colision>`.
        2. core.rfid.constants.TAG_ADMIN: llama a :meth:`tag_admin(tag) <tag_admin>`.
        3. Default: si el tag es distinto al que se había leído previamente entonces actualiza el tag y llama al maestro

        Arguments:
            tipo_lectura (str): el tipo de tag. Alguno de los :ref:`core.rfid.constants.tipo_tags`.
            tag (core.documentos.soporte_digital.SoporteDigital): instancia de ``SoporteDigital``
        """
        if tipo_lectura == TAG_COLISION:
            self.modulo.pantalla_insercion()
            self.tag_colision()
        elif tipo_lectura == TAG_ADMIN:
            self.tag_admin(tag)
        elif tipo_lectura == NO_TAG:
            self.no_tag(tag)
        else:
            if tag != self.tag_leido:
                self.tag_leido = tag
                self.maestro()

    def tag_colision(self):
        """
        Metodo que se llama cuando se detecta colision. Manda a expulsar la boleta.
        """
        self.expulsar_boleta("colision")

    def expulsar_boleta(self, motivo=""):
        """Metodo de expulsion de boleta."""
        self.sesion.logger.debug("EXPULSION dese modulo rampa (%s)", motivo)
        self.tiene_papel = False
        self.tag_leido = None
        if self.tiene_conexion:
            self._servicio.expulsar_boleta()

    def tag_admin(self, tag=None):
        """
        Metodo que se llama cuando se apoya un tag de admin. Expulsa la boleta (si la hay) y sale del modulo

        .. todo::
            El parámetro ``tag`` no se usa.

        Parameters:
            tag (core.documentos.soporte_digital.SoporteDigital): no se usa.

        """
        self.desregistrar_eventos()
        if self.tiene_papel:
            self.expulsar_boleta("tag_admin")
        self.modulo.salir()
    
    def no_tag(self, tag=None):
        """Metodo que se llama cuando se quita el tag del rfid."""
        pass

    def registrar_eventos(self):
        """Registra los eventos por default de la rampa."""
        self.registrar_default_lector()
        self.registrar_default_sensor_1()
        self.registrar_default_sensor_2()

        ## Los siguientes eventos están relacionados con presencia

        # evento que indica que se enchufó la máquina
        self.registrar_ac(self.modulo._recheck_plugged)
        # evento que indica que se desenchufó la máquina
        self.registrar_battery_discharging(self.modulo._recheck_unplugged)

    def desregistrar_eventos(self):
        """Desregistra los eventos por default de la rampa."""
        self.remover_consultar_lector()
        self.remover_insertando_papel()
        self.remover_nuevo_papel()
        ## Los siguientes eventos están relacionados con presencia
        self.remover_battery_discharging()
        self.remover_ac()

    @si_tiene_conexion
    def registrar_error_impresion(self, callback):
        """
        Registra un ``callback`` que se ejecuta cuando hay un error de impresión

        Args:
            callback (function): la funcion.

        """
        self._servicio.registrar_error_impresion(callback)

    @si_tiene_conexion
    def remover_error_impresion(self):
        """
        Desregistra el callback agregado por :meth:`registrar_error_impresion <registrar_error_impresion>`
        """

        self._servicio.remover_error_impresion()

    @si_tiene_conexion
    def registrar_fin_impresion(self, callback):
        """
        Registra un ``callback`` que se ejecuta cuando finaliza la impresión

        Args:
            callback (function): la funcion.

        """
        self._servicio.registrar_fin_impresion(callback)

    @si_tiene_conexion
    def remover_fin_impresion(self):
        self._servicio.remover_fin_impresion()

    @si_tiene_conexion
    def registrar_default_lector(self):
        """
        Registra la funcion :meth:`_cambio_tag <_cambio_tag>` como callback cuando el servicio
        :meth:`IPCClient <core.ipc.client.IPCClient>` detecta un cambio en el tag.
        """
        self._servicio.consultar_lector(self._cambio_tag)

    @si_tiene_conexion
    def remover_consultar_lector(self):
        """
        Desregistra el callback de atualizacion del tag.
        """
        self._servicio.remover_consultar_lector()

    def registrar_default_sensor_1(self):
        """
        Registra a :meth:`cambio_sensor_1 <cambio_sensor_1>` como callback del evento de insercion de papel en la
        rampa.
        """
        self.registrar_insertando_papel(self.cambio_sensor_1)

    def registrar_default_sensor_2(self):
        """
        Registra a :meth:`cambio_sensor_2 <cambio_sensor_2>` como callback del evento de nuevo papel (autofeed).
        """
        self.registrar_nuevo_papel(self.cambio_sensor_2)

    @si_tiene_conexion
    def registrar_nuevo_papel(self, callback):
        """
        Registra un ``callback`` para el evento de nuevo papel (autofeed).

        Args:
            callback (function): el callback

        """
        self._servicio.registrar_autofeed_end(callback)

    @si_tiene_conexion
    def registrar_sensor_rampa(self, callback):
        """Registra un ``callback`` al evento de sensor rampa."""
        self._servicio.registrar_sensor_rampa(callback)

    @si_tiene_conexion
    def consultar_tarjeta(self, callback):
        """Registra un ``callback`` al evento de consulta de tarjeta."""
        self._servicio.consultar_tarjeta(callback)

    @si_tiene_conexion
    def remover_consultar_tarjeta(self):
        """Remueve el ``callback`` del evento de consulta de tarjeta."""
        self._servicio.remover_consultar_tarjeta()

    @si_tiene_conexion
    def remover_nuevo_papel(self):
        """Remueve el ``callback`` del evento de nuevo papel."""
        self._servicio.remover_autofeed_end()

    @si_tiene_conexion
    def remover_sensor_rampa(self):
        """Remueve el ``callback`` del evento de sensor rampa."""
        self._servicio.remover_sensor_rampa()

    @si_tiene_conexion
    def remover_insertando_papel(self):
        """Remueve el ``callback`` del evento insertando papel"""
        self._servicio.remover_insertando_papel()

    @si_tiene_conexion
    def registrar_insertando_papel(self, callback):
        """Registra un ``callback`` al evento de consulta de tarjeta."""
        self._servicio.registrar_insertando_papel(callback)

    def registrar_boleta_expulsada(self, callback):
        """Registra un ``callback`` al evento de boleta expulsada."""
        self._servicio.registrar_boleta_expulsada(callback)

    def remover_boleta_expulsada(self):
        """Remueve el ``callback`` del evento de boleta expulsada"""
        self._servicio.remover_boleta_expulsada()

    def get_tag(self):
        """
        Obtiene el tag leido a traves de :meth:`core.ipc.client.IPCClient <core.ipc.client.IPCClient>`

        Returns:
            core.documentos.soporte_digital.SoporteDigital: el tag como ``SoporteDigital``.
        """
        self.tag_leido = self._servicio.get_tag()
        return self.tag_leido

    def get_tag_async(self, callback):
        """
        Manda a leer el tag de forma asíncrona al :class:`core.ipc.client.IPCClient <core.ipc.client.IPCClient>` y
        llama al ``callback`` pasandole como parámetro el
        :class:`SoporteDigital <core.documentos.soporte_digital.SoporteDigital>`.

        Args:
            callback (function): funcion a ejecutar cuando el tag es leído.

        .. function:: get_tag_async._inner(data)

            Funcion que se pasa como callback al evento de lectura del
            :class:`IPCClient <core.ipc.client.IPCClient>` y que ejecuta el ``callback``

            :param data: datos del tag
            :type data: int

        """
        def _inner(data):
            tag = self._servicio._parse_tag(data)
            self.tag_leido = tag
            callback(tag)

        self._servicio.call_async("read", _inner)

    def guardar_tag(self, tipo_tag, datos, quema):
        """
        Manda a guardar datos en un tag.

        Args:
            tipo_tag (str): alguno de los :ref:`core.rfid.constants.tipo_tags`
            datos (list[bytes]): datos a guardar en el tag.
            quema (bool): indica si se marca el tag como solo lectura o no.

        Returns:
            int: resultado del guardado del tag.
        """
        return self._servicio.guardar_tag(tipo_tag, datos, quema)

    def guardar_tag_async(self, callback, tipo_tag, datos, quema):
        """
        Hace lo mismo que :meth:`guardar_tag <guardar_tag>` pero de forma asíncrona llamando a un callback luego del
        guardado.

        Args:
            callback (function): funcion a llamar.
            tipo_tag (str): alguno de los :ref:`core.rfid.constants.tipo_tags`
            datos (list[bytes]): datos a guardar en el tag.
            quema (bool): indica si se marca el tag como solo lectura o no.

        Returns:

        """
        return self._servicio.guardar_tag_async(callback, tipo_tag, datos,
                                                quema)

    @si_tiene_conexion
    def reset_rfid(self):
        """
        Manda a resetear el dispositivo RFID llamando a
        :meth:`core.ipc.client.IPCClient.reset_rfid <core.ipc.client.IPCClient.reset_rfid>`
        """
        self._servicio.reset_rfid()

    @si_tiene_conexion
    def reset_printer(self):
        """
        Manda a resetear la impresora llamando a
        :meth:`core.ipc.client.IPCClient.reset <core.ipc.client.IPCClient.reset>`
        con :const:`core.armve.constants.DEV_PRINTER`

        """
        self._servicio.reset(DEV_PRINTER)

    def imprimir_serializado(self, tipo_tag, tag, transpose=False,
                             only_buffer=False, extra_data=None):
        """
        Manda a imprimir los datos de un tag. Llama a

        Args:
            tipo_tag (str): tipo del tag que se manda. Debe ser alguno de los :ref:`core.rfid.constants.tipo_tags`.
            tag (str): string en base64 con los datos del tag.
            transpose (bool): transponer imagen.
            only_buffer (bool): solo cargar el buffer de impresion.
            extra_data (any): datos extra para imprimir la imagen.
        """

        self._servicio.imprimir_serializado(tipo_tag, tag, transpose=transpose,
                                      only_buffer=only_buffer,
                                      extra_data=extra_data)

    @si_tiene_conexion
    def get_papel_listo(self):
        """
        Obtiene el estado del papel llamando a
        :meth:`core.ipc.client.IPCClient._estado_papel(ready=True) <core.ipc.client.IPCClient._estado_papel>`

        Returns:
            any: estado del papel
        """
        return self._servicio._estado_papel(ready=True)

    def get_arm_version(self):
        """
        Devuelve la version de ARM llamando a
        :meth:`core.ipc.client.IPCClient.get_arm_version() <core.ipc.client.IPCClient.get_arm_version>`

        Returns:
            str: la version
        """
        return self._servicio.get_arm_version()

    def get_arm_build(self):
        """
        Obtiene version de build del ARM llamando a
        :meth:`core.ipc.client.IPCClient.get_arm_build() <core.ipc.client.IPCClient.get_arm_build>`

        Returns:
            str: version de build

        """
        return self._servicio.get_arm_build()

    def get_antenna_level(self):
        """
        Obtiene la señal de la antena llamando a
         :meth:`core.ipc.client.IPCClient.get_arm_build() <core.ipc.client.IPCClient.get_arm_build>`

        Returns:
            float: señal de la antena

        """
        return self._servicio.get_antenna_level()

    def get_brightness(self):
        """
        Obtiene el nivel de brillo de la pantalla llamando a
         :meth:`core.ipc.client.IPCClient.get_brightness() <core.ipc.client.IPCClient.get_brightness>`

        Returns:
            float: nivel de brillo de la pantalla
        """
        return self._servicio.get_brightness()

    def set_brightness(self, value):
        """
        Establece el nivel de brillo de la pantalla llamando a
        :meth:`core.ipc.client.IPCClient.set_brightness() <core.ipc.client.IPCClient.set_brightness>`

        Args:
            value (int): valor del brillo a setear.

        Returns:
            any: el estado de la respuesta

        """
        return self._servicio.set_brightness(value)

    def get_actual_brightness(self):
        return self._servicio.get_actual_brightness()

    def set_actual_brightness(self, value):
        return self._servicio.set_actual_brightness(value)

    def get_fan_mode(self):
        """
        Obtiene el modo del ventilador llamando a
         :meth:`core.ipc.client.IPCClient.get_fan_mode() <core.ipc.client.IPCClient.get_fan_mode>`

        Returns:
            any: el modo en que se encuentra el ventilador
        """
        return self._servicio.get_fan_mode()

    def set_fan_mode(self, value):
        """
        Establece el modo del ventilador llamando a
         :meth:`core.ipc.client.IPCClient.get_fan_mode() <core.ipc.client.IPCClient.get_fan_mode>`

        Returns:
            any: el modo en que se encuentra el ventilador
        """
        return self._servicio.set_fan_mode(value)

    def get_fan_speed(self):
        """
        Obtiene la velocidad del ventilador llamando a
         :meth:`core.ipc.client.IPCClient.get_fan_speed() <core.ipc.client.IPCClient.get_fan_speed>`

        Returns:
            any: la velocidad
        """
        return self._servicio.get_fan_speed()

    def set_fan_speed(self, value):
        """
        Establece la velocidad del ventilador llamando a
         :meth:`core.ipc.client.IPCClient.set_fan_speed() <core.ipc.client.IPCClient.set_fan_speed>`

        Args:
            value (any): la velocidad

        Returns:
            any: resultado de la operacion.
        """
        return self._servicio.set_fan_speed(value)

    def reset(self, device):
        """
        Resetea un dispositivo.

        Args:
            device (int): id del dispositivo. Debe ser alguno de los core.armve.constants.dispositivos.

        Returns:
            any: resultado de reset.

        """
        return self._servicio.reset(device)

    def get_autofeed_mode(self):
        """
        Obtiene el modo de autofeed llamando a
        :meth:`core.ipc.client.IPCClient.get_autofeed_mode() <core.ipc.client.IPCClient.get_autofeed_mode>`

        Returns:
            any: modo autofeed
        """
        return self._servicio.get_autofeed_mode()

    def set_autofeed_mode(self, value):
        """
        Establece el modo de autofeed llamando a
        :meth:`core.ipc.client.IPCClient.set_autofeed_mode() <core.ipc.client.IPCClient.set_autofeed_mode>`

        Args:
            value: valor a establecer

        Returns:
            any: resultado del set
        """
        return self._servicio.set_autofeed_mode(value)

    def get_printer_quality(self):
        """
        Obtiene la calidad de la impresora llamando a
         :meth:`core.ipc.client.IPCClient.get_printer_quality() <core.ipc.client.IPCClient.get_printer_quality>`

        Returns:
            any: la calidad de la impresora
        """
        return self._servicio.get_printer_quality()

    def set_printer_quality(self, value):
        """
        Establece la calidad de la impresora llamando a
         :meth:`core.ipc.client.IPCClient.get_printer_quality() <core.ipc.client.IPCClient.get_printer_quality>`

        Args:
            value (any): valor a establecer

        Returns:
            any: la calidad de la impresora

        """

        return self._servicio.set_printer_quality(value)

    @si_tiene_conexion
    def registrar_reset_device(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_reset_device`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_reset_device(callback)

    @si_tiene_conexion
    def remover_reset_device(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_reset_device`
        """
        self._servicio.remover_reset_device()

    @si_tiene_conexion
    def registrar_ac(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_ac`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_ac(callback)

    @si_tiene_conexion
    def registrar_battery_discharging(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_battery_discharging`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_battery_discharging(callback)

    @si_tiene_conexion
    def registrar_battery_plugged(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_battery_plugged`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_battery_plugged(callback)

    @si_tiene_conexion
    def registrar_battery_unplugged(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_battery_unplugged`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_battery_unplugged(callback)

    @si_tiene_conexion
    def registrar_pir_detected(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_pir_detected`
        """
        self._servicio.registrar_pir_detected(callback)

    @si_tiene_conexion
    def registrar_pir_not_detected(self, callback):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.registrar_pir_not_detected`

        Args:
            callback (function): se llama cuando se dispara el evento.
        """
        self._servicio.registrar_pir_not_detected(callback)

    @si_tiene_conexion
    def remover_ac(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_ac`
        """
        self._servicio.remover_ac()

    @si_tiene_conexion
    def remover_battery_discharging(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_battery_discharging`
        """
        self._servicio.remover_battery_discharging()

    @si_tiene_conexion
    def remover_battery_plugged(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_battery_plugged`
        """
        self._servicio.remover_battery_plugged()

    @si_tiene_conexion
    def remover_battery_unplugged(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_battery_unplugged`
        """
        self._servicio.remover_battery_unplugged()

    @si_tiene_conexion
    def remover_pir_detected(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_pir_detected`
        """
        self._servicio.remover_pir_detected()

    @si_tiene_conexion
    def remover_pir_not_detected(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.remover_pir_not_detected`
        """
        self._servicio.remover_pir_not_detected()

    def get_power_source(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.get_power_source`
        """
        return self._servicio.get_power_source()

    def get_power_status(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.get_power_status`
        """
        return self._servicio.get_power_status()

    def get_pir_status(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.get_pir_status`
        """
        return self._servicio.get_pir_status()

    def get_pir_mode(self):
        """
        Llama al método

        :meth:`core.ipc.client.IPCClient.get_pir_mode`
        """
        return self._servicio.get_pir_mode()

    @si_tiene_conexion
    def get_presencia_status(self):
        return self._servicio.get_presence_status()

    @si_tiene_conexion
    def get_presencia_mode(self):
        return self._servicio.get_presencia_mode()

    @si_tiene_conexion
    def set_presencia_mode(self, value):
        self._servicio.set_presencia_mode(value)

    @si_tiene_conexion
    def set_backlight_status(self, value):
        self._servicio.set_backlight_status(value)
    
    def encender_pantalla(self):
        self.set_backlight_status(True)

    @si_tiene_conexion
    @presencia_on_required
    def presence_reset(self, value):
        """
        Enviamos una señal para avisar que hubo presencia
        por medio del dispositivo Touch
        """
        self.sesion.logger.warning('RESET!!')
        self._servicio.presence_reset(value)
    
    @si_tiene_conexion
    def registrar_presencia(self):
        modulo = self.modulo
        self.registrar_presence_changed(modulo._cambio_presencia)
    
    @si_tiene_conexion
    def registrar_presence_changed(self, callback):
        self._servicio.registrar_presence_changed(callback)
    
    @si_tiene_conexion
    def remover_presence_changed(self):
        self._servicio.remover_presence_changed()

    @si_tiene_conexion
    def set_led_action(self, action, next_action=None):
        return self._servicio.set_led_action(action, next_action)

    @si_tiene_conexion
    def get_estado_leds(self):
        return self._servicio.get_estado_leds()


class RampaActas(RampaBase):

    """
    Rampa genérica para el módulo de Apertura y el Cierre, ya que ambos usan el
    controlador de interación y manejan de una manera similar la toma de papel.
    """

    @semaforo
    def maestro(self):
        """
        El maestro de ceremonias, el que dice que se hace y que no.

        Se verifican algunas cuestiones:

            * Si el tipo de tag es de recuento, voto, vacío o de apertura, se intentará
            procesar.

            * Sino, si el estado del módulo es ``CARGA``, ``CONFIRMACIÓN`` o ``SETUP``,
            se verifica si el nombre del módulo es diferente a ``SUBMODULO DATOS ESCRUTINIO``.
            Si es True, se reinicia el módulo, caso contrario se procede a expulsar la
            boleta.

            * Sino, si el estado del módulo es ``INICIAL``` , hay papel y no hay tag leído,
            se procede a expulsar la boleta.

            * Por último, si es ninguno de los casos anteriores, se verifica si el
            estado del módulo es distinto a ```REGISTRANDO``. Si es así se muestra el
            mensaje inicial.

        """
        if self.tag_leido is not None \
                and (self.tag_leido.tipo in (TAG_RECUENTO, TAG_VOTO,
                                             TAG_VACIO, TAG_APERTURA)):
            try:
                self.procesar_tag(self.tag_leido)
            except MesaNoEncontrada:
                self.expulsar_boleta("mesa_no_encontrada")
        elif self.modulo.estado in (E_CARGA, E_CONFIRMACION, E_SETUP):
            if self.modulo.nombre != SUBMODULO_DATOS_ESCRUTINIO:
                self.modulo.reiniciar_modulo()
            else:
                self.expulsar_boleta("submodulo_datos_escrutinio")
        elif self.modulo.estado == E_INICIAL and self.tiene_papel and \
                self.tag_leido is None:
            def _expulsar():
                if self.tiene_papel and self.tag_leido is None:
                    self.expulsar_boleta("inicial")
            timeout_add(1000, _expulsar)
        elif self.modulo.estado != E_REGISTRANDO:
            self.modulo.mensaje_inicial()
