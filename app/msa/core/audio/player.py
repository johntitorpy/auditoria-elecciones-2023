""" audioplayer.py
    Módulo para reproducción de archivos de sonido vía ALSA
"""
# Importante para el cálculo del sleep en run()
import time

from alsaaudio import PCM, Mixer, ALSAAudioError, MIXER_CHANNEL_ALL
from threading import Thread

from msa.core.logging import get_logger
from msa.core.audio.settings import SPEECH_PAUSE
from msa.core.audio.constants import VALORES_VOLUMEN, MIXER_PRIO
from pygame import mixer

logger = get_logger("core")


class AudioPlayer(Thread):
    """Un thread que ejecuta archivos de sonido.

    A medida que recibe mensajes para reproducir archivos, los guarda en
    un cache interno asi no los tiene que cargar en cada repeticion.

    Para ejecutar un wav, se debe llamar al metodo play(file), donde file
    es la direccion completa al archivo wav. También se pueden encolar
    varios wav a decir en una lista mediante el método queue_play().
    """

    PAUSE_TOKEN = ""

    def __init__(self, as_daemon=True):
        Thread.__init__(self)
        # Se establece SampleRate en 22050 para que concida con el valor con
        # el que polly los genera por defecto.
        mixer.init(22050)
        self.daemon = as_daemon
        self._cache = {}
        self.__running = False
        self._device = None
        self._mixers = {}
        self._default_mixer = None
        self._queue = []
        self.__init_alsa()
        self.callback_fin_cola = None

    def __init_alsa(self):
        try:
            self._device = PCM()
        except ALSAAudioError as e:
            logger.error("ERROR: Error al inicializar dispositivo ALSA: %s" % str(e))
            return
        else:
            for mixer in MIXER_PRIO:
                try:
                    self._mixers[mixer] = Mixer(mixer)
                except ALSAAudioError as e:
                    err = "Warning: Error al inicializar mixer ALSA: %s"
                    logger.warning(err % str(e))
                else:
                    if self._default_mixer is None:
                        self._default_mixer = mixer

    def _play(self, audio):
        """
        Plays a sound, using pygame. See
        https://groups.google.com/g/pygame-mirror-on-google-groups/c/YgabvG4ib1A?pli=1
        """
        s = mixer.Sound(audio)
        c = s.play()
        while c.get_busy():
            pass
        c.stop()
        s.stop()

    def run(self):
        """Starts the loop waiting for audio files to be played"""
        self.__running = True
        while self.__running:
            if len(self._queue):
                now_filename, now_message = self._queue.pop(0)
                if now_message == AudioPlayer.PAUSE_TOKEN:
                    time.sleep(SPEECH_PAUSE)
                    continue
                with open(now_filename) as audio:
                    self._play(audio)
                if not len(self._queue) and self.callback_fin_cola is not None:
                    self.callback_fin_cola()
            time.sleep(0.1)

    def play(self, _file):
        """Assigns a e file to be played.

        Arguments:
        _file -- File path of the audio file.
        """
        if _file is not None:
            self._queue = [(_file, None)]

    def queue_play(self, _file, mensaje=None):
        if _file is not None:
            self._queue.append((_file, mensaje))

    def empty_queue(self):
        self._queue = []

    def stop(self):
        """Stops the thread. It can't be started again, so it also closes
        the opened audio device"""
        self.empty_queue()
        self.__running = False
        self.close()

    def pending_files(self):
        return len(self._queue) > 0

    def close(self):
        """Closes the audio output opened in the constructor.
        Useful to call from outside if as_daemon=False
        (instantiated only to set the volume for example)
        """
        if self._device:
            self._device.close()

    def set_volume(self, level):
        """Sets volume"""
        mixer_name = self._default_mixer
        num_vals = len(VALORES_VOLUMEN)
        if mixer_name is not None and level >= 0 and level <= num_vals:
            mixer = self._mixers[mixer_name]
            log_value = VALORES_VOLUMEN[level]
            mixer.setvolume(log_value, MIXER_CHANNEL_ALL)

    def get_volume(self, mixer=None):
        """Returns the volume in a Mixer. If mixer is None, returns the volume
        from the most relevant, the default"""
        index = None
        if mixer is None:
            mixer = self._default_mixer
        if mixer is not None:
            log_value = int(self._mixers[mixer].getvolume()[0])
            try:
                index = VALORES_VOLUMEN.index(log_value)
            except ValueError:
                pass
        return index

    def registrar_callback_fin_cola(self, callback):
        """Registra un callback que será llamado la próxima vez que se vacíe la
        cola de mensajes."""

        def _inner():
            callback()
            self.callback_fin_cola = None

        self.callback_fin_cola = _inner
