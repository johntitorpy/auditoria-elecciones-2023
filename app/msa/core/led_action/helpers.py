class Dummy():
    """Clase dummy que no hace nada, se utiliza para la compatibilidad P4/P6"""
    def dummy(*args, **kw): pass
    def __getattr__(self, _): return self.dummy
