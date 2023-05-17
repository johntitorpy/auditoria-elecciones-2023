# coding: utf-8
from __future__ import absolute_import
from __future__ import print_function

try:
    import colorama
except ImportError:
    colorama = None
    pass
import os
import sys

from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO
from logging.handlers import (
    SocketHandler,
    DEFAULT_TCP_LOGGING_PORT,
    RotatingFileHandler,
)
from types import MethodType

from msa.core.logging.settings import (
    DEFAULT_LOG_LEVEL,
    LOGGING_SERVER_HOST,
    FILELOG_SIZE,
    FILELOG_ROTATION,
    LOG_TO_FILE,
    LOG_NAME,
    LOG_TO_DB,
    LOG_TO_STDOUT,
    LOG_TO_SENTRY,
    LOG_SENTRY_PATH,
    LOG_TO_LOGSTASH,
    LOG_CAPTURE_STDOUT,
    LOGSTASH_HOST,
    LOGSTASH_PORT,
    LOGSTASH_ENVIRONMENT,
    LOGSTASH_DB_PATH,
    LOGSTASH_LOG_LEVEL,
    LOGSTASH_TRANSPORT,
    LOGSTASH_ASYNC,
)

loggers = {}


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=DEFAULT_LOG_LEVEL):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def debug_armve(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'DEBUG'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    logger.debug_armve("Houston, we have a %s", "thorny problem", exc_info=1)
    """
    try:
        if self.isEnabledFor(DEBUG):
            if colorama:
                stream = args[0].split(" ")
                data = colorama.Fore.WHITE + stream[0] + " "
                data += colorama.Fore.YELLOW + " ".join(stream[1:4]) + " "
                data += colorama.Fore.GREEN + stream[4] + " "
                data += colorama.Fore.BLUE + " ".join(stream[5:7]) + " "
                resto = stream[7:]
                nuevo_resto = []
                prox_cambio = 0
                for i, elem in enumerate(resto):
                    if elem == "e0" and resto[i + 1] == "04":
                        color = colorama.Fore.RED
                        prox_cambio = i + 8
                    elif prox_cambio == i:
                        color = colorama.Fore.MAGENTA
                    nuevo_resto.append(color + elem)
                data += " ".join(nuevo_resto)
            else:
                data = args[0]

            self._log(DEBUG, msg, (data,), **kwargs)
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except Exception:
        pass


def get_logger(name):
    # El root logger debe estar en debug para que se respete el level de log de cada handler individual
    if len(loggers) == 0:
        getLogger().setLevel(DEBUG)
    logger = loggers.get(name)
    if logger is None:
        logger = getLogger(name)
        logger.setLevel(DEBUG)  # opcional
        setattr(logger, "debug_armve", debug_armve)
        logger.debug_armve = MethodType(debug_armve, logger)

        # Le asociamos los handlers
        if LOG_TO_DB:
            add_socket_handler(logger)
        if LOG_TO_FILE:
            add_file_handler(logger)
        if LOG_TO_STDOUT and not LOG_CAPTURE_STDOUT:
            add_stdout_handler(logger)
        if LOG_TO_SENTRY:
            add_raven_logger(logger, LOG_SENTRY_PATH)
        if LOG_TO_LOGSTASH:
            add_logstash_handler(logger, name)
        loggers[name] = logger
    return logger


def add_socket_handler(logger):
    handler = SocketHandler(LOGGING_SERVER_HOST, DEFAULT_TCP_LOGGING_PORT)
    if DEFAULT_LOG_LEVEL == DEBUG:
        logger.addHandler(handler)


def add_file_handler(logger):
    formatter = Formatter(
        "[%(asctime)s] %(name)s %(funcName)s():%(lineno)d\t%(message)s"
    )
    formatter.default_time_format = "%S"
    try:
        if DEFAULT_LOG_LEVEL == DEBUG:
            log_file = LOG_NAME % logger.name.lower()
            if not os.path.exists(log_file):
                try:
                    open(log_file, "w").close()
                except IOError:
                    pass
            handler = RotatingFileHandler(
                log_file, maxBytes=FILELOG_SIZE, backupCount=FILELOG_ROTATION
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    except IOError:
        print(("La ubicacion %s no existe" % log_file))


def add_stdout_handler(logger):
    formatter = Formatter(
        "[%(asctime)s.%(msecs)d] %(name)s %(funcName)s():%(lineno)d\t%(message)s"
    )
    try:
        # Si está instalado rainbow_logging_handler (coloriza el output
        # de consola) lo usamos, sino defaulteamos al módulo logging
        from rainbow_logging_handler import RainbowLoggingHandler

        handler = RainbowLoggingHandler(
            sys.stderr, color_funcName=("black", "black", True)
        )
    except ImportError:
        handler = StreamHandler()
        pass

    handler.setFormatter(formatter)
    handler.setLevel(DEFAULT_LOG_LEVEL)
    logger.addHandler(handler)


def add_raven_logger(logger, raven_url):
    from raven.base import Client
    from raven.handlers.logging import SentryHandler

    if DEFAULT_LOG_LEVEL == DEBUG:
        client = Client(raven_url, auto_log_stacks=True)
        handler = SentryHandler(client)
        logger.addHandler(handler)


def add_logstash_handler(logger, name):
    # Por ahora solo se usa logstash en credenciales
    if name != "credenciales":
        return

    from logstash_async.handler import SynchronousLogstashHandler, AsynchronousLogstashHandler
    from logstash_async.formatter import LogstashFormatter

    if LOGSTASH_ASYNC:
        logstash_logger = AsynchronousLogstashHandler(
            host=LOGSTASH_HOST,
            port=LOGSTASH_PORT,
            database_path=LOGSTASH_DB_PATH % (name),
            transport=LOGSTASH_TRANSPORT,
        )
    else:
        logstash_logger = SynchronousLogstashHandler(
            host=LOGSTASH_HOST,
            port=LOGSTASH_PORT,
            transport=LOGSTASH_TRANSPORT,
        )
    logstash_formatter = LogstashFormatter(
        extra=dict(application=name, environment=LOGSTASH_ENVIRONMENT)
    )
    logstash_logger.setLevel(LOGSTASH_LOG_LEVEL)
    logstash_logger.setFormatter(logstash_formatter)

    logger.addHandler(logstash_logger)
