# memory_manager.py - Asignador de direcciones virtuales para Patito

class MemoryManager:
    RANGES = {
        'global':    {'entero': (1000, 1999), 'flotante': (2000, 2999), 'bool': (3000, 3999)},
        'local':     {'entero': (4000, 4999), 'flotante': (5000, 5999), 'bool': (6000, 6999)},
        'temporal':  {'entero': (7000, 7999), 'flotante': (8000, 8999), 'bool': (9000, 9999)},
        'constante': {'entero': (10000, 10999), 'flotante': (11000, 11999),
                      'bool': (12000, 12999), 'string': (13000, 13999)},
    }

    def __init__(self):
        self._counters = {
            seg: {t: start for t, (start, _) in tipos.items()}
            for seg, tipos in self.RANGES.items()
        }
        self._constantes = {}  # valor -> dirección

    def _asignar(self, segmento, tipo):
        addr = self._counters[segmento][tipo]
        _, limite = self.RANGES[segmento][tipo]
        if addr > limite:
            raise Exception(f"Memoria agotada: segmento {segmento}, tipo {tipo}")
        self._counters[segmento][tipo] += 1
        return addr

    def asignar_global(self, tipo):
        return self._asignar('global', tipo)

    def asignar_local(self, tipo):
        return self._asignar('local', tipo)

    def asignar_temporal(self, tipo):
        return self._asignar('temporal', tipo)

    def asignar_constante(self, valor, tipo):
        key = (valor, tipo)
        if key not in self._constantes:
            self._constantes[key] = self._asignar('constante', tipo)
        return self._constantes[key]

    def reset_local(self):
        """Llama esto al terminar de compilar cada función."""
        for tipo, (start, _) in self.RANGES['local'].items():
            self._counters['local'][tipo] = start
        for tipo, (start, _) in self.RANGES['temporal'].items():
            self._counters['temporal'][tipo] = start