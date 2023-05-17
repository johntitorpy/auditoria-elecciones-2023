from __future__ import absolute_import
from time import sleep

from construct.core import FieldError

from msa.core.armve.constants import MSG_ERROR


def arm_command(command):
    def _arm_command(function):
        def _inner(self, *args, **kwargs):
            function(self, *args, **kwargs)
            response = self.read(expecting_command=command)
            return response
        return _inner
    return _arm_command


def arm_event(function):
    def _inner(self, *args, **kwargs):
        function(self, *args, **kwargs)
        try:
            self.read()
        except FieldError:
            pass
    return _inner

def arm_event_response(function):
    def _inner(self, data, *args, **kwargs):
        # la suscripción a eventos no devuelve datos adicionales:
        if data:
            return function(self, data, *args, **kwargs)
    return _inner

def retry_on_error(function):
    def _inner(self, *args, **kwargs):
        tries = 0
        response = function(self, *args, **kwargs)
        while tries < 2 and response is not None and response[3] == MSG_ERROR:
            sleep(0.1)
            response = function(self, *args, **kwargs)
            tries += 1
        return response
    return _inner


def wait_for_response(command,max_retries=5):
    def _arm_command(function):
        def _inner(self, *args, **kwargs):
            tries = 0
            response = function(self, *args, **kwargs)
            while tries <= max_retries:
                sleep(0.1)
                response = self.read(expecting_command=command)
                if response is not None:
                    return response
                else:
                    tries += 1
            return response
        return _inner
    return _arm_command
