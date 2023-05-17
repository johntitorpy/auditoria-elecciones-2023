from functools import wraps

def en_pantalla(function):
    """Decora un metodo para que devuelva una señal."""
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if self.config_vista("en_pantalla"):
            return function(self, *args, **kwargs)
        else:
            return None
    return wrapper