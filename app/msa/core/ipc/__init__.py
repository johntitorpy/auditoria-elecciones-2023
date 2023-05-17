import os
from os import mkfifo
from time import sleep
from ujson import dumps, loads

from gi.repository.GLib import IOChannel, IOCondition, Error

from msa.core.logging import get_logger

class IPC():
    """Clase base de la comunicacion entre procesos.
    """
    def __init__(self, in_path, out_path, callback_lectura):
        assert in_path is not None
        assert out_path is not None
        assert callback_lectura is not None

        self.logger = get_logger("ipc")
        self.in_path = in_path
        self.out_path = out_path
        self.callback_lectura = callback_lectura
        self.init_channels()
        self.registrar_evento()
        #self.waiting_response = False
        #self._response = -1
        self.waiting_response = {}
        self._response = {}

    def dumps(self, datos):
        """Serializador de mensajes."""
        # Provee compatibilidad con aquellas versiones de 'ujson' que no admiten
        # el parámetro 'reject_bytes'.
        try:
            return dumps(datos, reject_bytes=False)
        except:
            return dumps(datos)

    def loads(self, datos):
        """Desserializador de mensajes."""
        return loads(datos)

    def registrar_evento(self):
        """Registra el evento de lectura."""
        # pasamos user_data en True para poder distingir las notificaciones:
        self.in_channel.add_watch(IOCondition.IN, self.read_channel, True)

    def init_channels(self):
        """Inicializa los canales de comunicacion (entrada y salida)."""
        self.logger.debug("Iniciando pipes %s %s", self.in_path, self.out_path)
        try:
            # Si no existe el Pipe lo creamos
            try:
                mkfifo(self.in_path)
            except FileExistsError:
                pass
            # Traemos el file descriptor de lectura en modo no bloqueante.
            in_file = os.open(self.in_path, os.O_RDONLY|os.O_NONBLOCK)
            # Inicializamos en IOChannel de Glib.
            # https://lazka.github.io/pgi-docs/#GLib-2.0/classes/IOChannel.html#GLib.IOChannel.unix_new
            self.in_channel = IOChannel.unix_new(in_file)
            # Por las dudas borramos todos los mensajes y no hacemos nada con
            # ellos.
            self.in_channel.readlines()

            # Si no existe el Pipe lo creamos
            try:
                mkfifo(self.out_path)
            except (FileExistsError, Error):
                pass
            # Traemos el file descriptor de escritura (espera al otro extremo)
            out_file = os.open(self.out_path, os.O_WRONLY)
            # Inicializamos en IOChannel de Glib.
            self.out_channel = IOChannel.unix_new(out_file)
        except:
            self.logger.exception("Excepción al inicializar pipes")
            raise
        self.logger.debug("Listo pipes... %s %s", self.in_path, self.out_path)

    def send(self, msg_type, signal, params, silent=0):
        """Envia un mensaje por el canal.

        Argumentos:
            msg_type - tipo de mensaje: "request", "event", "response", "test"
            signal - nombre del evento o método
            params - lista de parámetros
            silent - 1: no debug log
        """
        try:
            self.out_channel.flush()
        except Exception:
            self.logger.exception("Excepción al enviar por el pipe")
            self.init_channels()

        # generamos el mensaje a enviar (string serializado):
        mensaje = self.dumps([msg_type, signal, params, silent])
        msg = bytes(mensaje + "\n", "utf8")
        if not silent:
            self.logger.debug("---> Enviado mensaje {}".format(msg[:20]))
        try:
            self.out_channel.write_chars(msg, len(msg))
            self.out_channel.flush()
        except Exception:
            self.logger.exception("Excepción al enviar por el pipe")
            raise

    def read_channel(self, channel, user_data=None, *args, **kwargs):
        """Lee todos los mensajes en el canal.

        Argumentos:
            channel -- el canal de lectura.
        """
        # leemos todas las lineas
        try:
            data = channel.readlines()
        except Exception:
            self.logger.exception("Excepción al leer por el pipe")
            raise
        finally:
            # agregamos el watcher al canal (sólo si recibimos la notificación)
            if user_data:
                self.registrar_evento()
        # recorremos todas las lineas ya que hay un mensaje por linea.
        for datum in data:
            if datum != '':
                # limpiamos el mensaje
                callback_params = datum.strip()
                # parseamos el mensaje
                msg_type, signal, params, silent = self.loads(callback_params)
                if not silent:
                    self.logger.debug(">>> %s %s %s", msg_type, signal, params)
                # y llamamos al callback adecuado
                if signal in self.waiting_response and msg_type == "response":
                    func = self.procesar_respuesta
                else:
                    func = self.callback_lectura

                func(self, msg_type, signal, params)

    def procesar_respuesta(self, channel, rsp_type, signal, params):
        """Procesa la respuesta que estamos esperando."""
        self.waiting_response.pop(signal)
        self._response[signal] = params

    def get_ipc_method(self, method, wait_response=False, timeout=8, silent=0):
        """ Devuelve un metodo de IPC.

        Argumentos:
            method -- el nombre de la funcion que queremos llamar.
            waiting_response -- un booleano que representa si queremos esperar
                la respuesta o no
            timeout -- tiempo máximo a esperar respuesta (en segundos, aprox)
            silent -- no debug log
        """
        def _inner(params=None):
            ret = None
            self.waiting_response[method] = wait_response

            self.send("request", method, params, silent)

            if self.waiting_response[method]:
                tries = 0
                while tries < timeout * 10:
                    self.read_channel(self.in_channel)
                    if method not in self._response:
                        sleep(0.1)
                        tries += 1
                    else:
                        ret = self._response[method]
                        self._response.pop(method)
                        break
            return ret
        return _inner
