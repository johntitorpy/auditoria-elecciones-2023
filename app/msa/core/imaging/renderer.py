import os
import re
import signal
import sys
import time
from threading import Thread, Lock
from multiprocessing import get_context, set_start_method, Queue, Process
from io import BytesIO
from PIL import Image
from base64 import b64decode

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.0")
from gi.repository import Gtk, WebKit2, GLib

from functools import wraps
import traceback
from json import dumps, loads
from urllib.parse import unquote

from msa.core.logging import get_logger

logger = get_logger("renderer")

E_INICIAL = "INICIAL"
E_LISTO = "LISTO_P_RENDERIZAR"
E_RENDERIZANDO = "RENDERIZANDO"
E_ERROR = "ERROR_DESCONOCIDO"

TIMEOUT_INICIAL = 5
MAX_REINTENTOS_RENDERIZADO = 2


def get_traceback(e):
    lines = traceback.format_exception(type(e), e, e.__traceback__)
    return ''.join(lines)


def process_alive(func):
    """
        Decorador que pregunta si el proceso (Process)
        aún está vivo, de lo contrario vuelve a ejecutar
        el método para crear nuevas queues y un nuevo proceso.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0]._p.is_alive():
            args[0].create_process()
        func(*args, **kwargs)

    return wrapper


def is_running(pid) -> bool:
    """
        Función diseñada exclusivamente para Unix.
        Busca si existe la carpeta con el PID asociado
        al proceso padre (quien instancia Renderer).
    """
    if os.path.isdir('/proc/{}'.format(pid)):
        return True
    return False


def thread_status(ppid, pid_process):
    """
        Este método lo ejecuta un thread.

        Consulta si el proceso padre se encuentra vivo.
        Solo si el ppid no se encuentra vivo, se enviará
        una señal para finalizar el Process que lanzó este Thread
    """
    while is_running(ppid):
        time.sleep(5)
    else:
        os.kill(pid_process, signal.SIGTERM)


def listo_p_renderizar(obj, request) -> None:
    logger.info("Proceso de renderizado en funcionamiento")
    obj._id_estado = E_LISTO
    obj._lock.release()


def imagen_cargada(obj, request) -> None:
    img_base64 = request.split('/imagen_cargada/')[1].replace("data:image/png;base64,", "")
    buf = b64decode(img_base64)
    obj._id_estado = E_LISTO
    obj.result_queue.put(buf)
    obj._lock.release()


def error_overflow(obj, request) -> None:
    if obj._overflow_logs is None:
        obj._overflow_logs = open('/tmp/resultados_test_boletas.csv', mode='a')
    _overflow = request.split('/error_overflow/')[1].strip()
    dict_overflow = loads(unquote(_overflow))
    logger.info("Se detectó overflow en la boleta {}".format(dict_overflow['cod_datos']))
    obj._overflow_logs.write(str(dict_overflow) + '\n')
    obj._overflow_logs.flush()


class RendererConnClosed(Exception):
    pass


class RendererError(Exception):
    pass


class ThreadRender(Thread):
    """
        Clase para manejar las peticiones de renderizado
        que son enviadas a la webview a través de la ejecución
        de una función JavaScript enviando un json por parámetro.
    """

    def __init__(self, window, webview, to_render_queue, result_queue):
        """
            Args:
                daemon (bool): sí es True, garantiza que al cerrarse
                               el proceso padre, el hilo también finalice.
                window (Gtk.Window): ventana Gtk.
                webview (WebKit2.WebView): webview en donde se renderiza la boleta.
                to_render_queue (Queue): se alojan los datos obtenidos desde ImagenBoleta
                result_queue (Queue): se aloja la imagen ya renderizada en base64
                _id_estado (str): manejo de estados por los que pasa el proceso
                _locK (Lock): bloqueo que garantiza que la webview esté lista para enviar
                              a renderizar; asimismo, si se encuentra renderizando que no
                              tome nuevamente datos de la cola hasta que se haya obtenido
                              el resultado anterior.
        """
        super().__init__()
        self.daemon = True
        self.window = window
        self.webview = webview
        self.to_render_queue = to_render_queue
        self.result_queue = result_queue
        self._request_methods = {
            'listo_p_renderizar': listo_p_renderizar,
            'imagen_cargada': imagen_cargada
        }
        self._id_estado = E_INICIAL
        self._lock = Lock()
        self._lock.acquire()
        self._overflow_logs = None

    def run(self):
        def _resource_load_started(web_view, resource, request) -> None:
            request = request.get_uri()
            req = re.findall("listo_p_renderizar|imagen_cargada|error_overflow", request)
            if req:
                self._request_methods[req[0]](self, request)

        self.webview.connect('resource-load-started', _resource_load_started)
        finalizar = False
        while not finalizar:
            try:
                self._lock.acquire()
                data = self.to_render_queue.get()
                self._id_estado = E_RENDERIZANDO
                json_data = dumps(data, check_circular=False)
                GLib.idle_add(self.webview.run_javascript, f"render('{json_data}')", None, None, None)
            except Exception as e:
                logger.info(get_traceback(e), flush=True)

    def set_estado(self, estado) -> None:
        self._id_estado = estado

    def get_estado(self):
        return self._id_estado

    def __del__(self):
        sys.exit(0)


class Renderer:
    """
        Clase principal para manejar el renderizado de imágenes de boletas y actas
    """

    def __init__(self, uri: str, thread_render_class=None) -> None:
        """
            Inicializa los Queue y ejecuta el proceso de renderizado.

            Args:
                uri (str): Path al boleta.html encargado de renderizar un HTML
                pid (int): Número de proceso actual
                to_render_queue (Queue): cola para enviar los datos a renderizar
                result_queue (Queue): cola para recibir el base64 renderizado
                _p (Process): proceso de renderizado (spawn)
                _image (Image): Propiedad que guarda la última imagen obtenida.
        """
        try:
            set_start_method('spawn')
        except Exception as e:
            if 'context has already been set' not in str(e):
                raise e

        self._uri = uri
        self.pid = os.getpid()
        self._to_render_queue = None
        self._result_queue = None
        self._p = None
        self._image = None
        self._thread_render_class = ThreadRender
        if thread_render_class:
            self._thread_render_class = thread_render_class
        self._start()

    def _start(self) -> None:
        self.create_process()

    def create_process(self) -> None:
        """
            La función que crea el proceso de renderizado
            y las colas de comunicación
        """
        if self._p is not None:
            self._p.terminate()
            self._p.join()
            self._p.close()

        if 'DISPLAY' not in os.environ or os.environ['DISPLAY'] == '':
            os.environ['DISPLAY'] = ":0"

        self._result_queue = Queue(maxsize=1)
        self._to_render_queue = Queue(maxsize=1)
        self._p = Process(target=self._init_thread_and_start_gtk,
                          args=(self._uri, self._to_render_queue, self._result_queue,
                                self.pid, self._thread_render_class),
                          daemon=True)
        self._p.start()

    @staticmethod
    def create_window(uri, debug=False):
        window = Gtk.Window(
            default_width=2300,
            default_height=832
        )
        webview = WebKit2.WebView()
        settings = WebKit2.Settings()
        webview.set_settings(settings)
        settings.set_allow_file_access_from_file_urls(True)
        webview.load_uri(uri=f"file://{uri}")
        window.add(webview)
        if debug:
            settings.set_enable_developer_extras(True)
            window.show_all()
        return window, webview

    @staticmethod
    def _init_thread_and_start_gtk(uri, to_render_queue, result_queue, ppid, thread_render_class) -> None:
        """
            La función que ejecuta el proceso. Crea la webview e inicializa el hilo
            que va a tomar la data enviada a través del Queue.

            Setea la variable de entorno 'DISPLAY' porque al ejecutarse dentro del armve service,
            dentro de la iso esta variable nunca se setea.

            Ejecuta Gtk.main() para inicializar las ventanas.

            Args:
                to_render_queue (Queue): cola para enviar los datos a renderizar por el proceso hijo
                result_queue (Queue): cola para recibir el base64 renderizado
                uri (str): Path al html que se debe cargar.
                ppid (int): PID del proceso principal.
        """
        window, webview = Renderer.create_window(uri, debug=False)
        _thread = thread_render_class(window, webview, to_render_queue, result_queue)
        _thread.start()

        pid = os.getpid()  # Obtiene PID del Process que lanza el Thread
        _ = Thread(target=thread_status, args=(ppid, pid), daemon=True)
        _.start()

        window.connect('destroy', Gtk.main_quit)
        Gtk.main()

    @process_alive
    def prepare_image(self, data: dict) -> None:
        _finalizar = False
        while not _finalizar:
            if not self._to_render_queue.full():
                self._to_render_queue.put(data)
                _finalizar = True

    @process_alive
    def wait_result(self, timeout=5) -> None:
        try:
            result = self._result_queue.get(timeout=timeout)
            self._image = Image.open(BytesIO(result))
        except Exception as e:
            logger.exception(e)
            raise RendererConnClosed("Error al obtener el resultado")

    def get_result(self) -> Image:
        return self._image

    def fetch_result(self, data) -> Image:
        _finalizar = False
        intentos = 1
        while not _finalizar and intentos <= MAX_REINTENTOS_RENDERIZADO:
            logger.info('Intento renderizado {} con timeout {}'.format(intentos, TIMEOUT_INICIAL * intentos))
            try:
                self.prepare_image(data)
                self.wait_result(timeout=TIMEOUT_INICIAL * intentos)
                _finalizar = True
            except Exception as e:
                self.create_process()
                intentos += 1

        if not _finalizar and intentos > MAX_REINTENTOS_RENDERIZADO:
            raise RendererError('Maxima cantidad de intentos de renderizado alcanzado')

        return self.get_result()
