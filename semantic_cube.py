class SemanticCube:
    """
    Valida operaciones entre tipos de datos y regresa el tipo resultante.
    Si una operación no es válida, regresa None.
    """

    def __init__(self):
        self.cube = {
            # Operaciones aritméticas con enteros
            ('entero', '+', 'entero'): 'entero',
            ('entero', '-', 'entero'): 'entero',
            ('entero', '*', 'entero'): 'entero',
            ('entero', '/', 'entero'): 'flotante',

            # Operaciones aritméticas con flotantes
            ('flotante', '+', 'flotante'): 'flotante',
            ('flotante', '-', 'flotante'): 'flotante',
            ('flotante', '*', 'flotante'): 'flotante',
            ('flotante', '/', 'flotante'): 'flotante',

            # Operaciones mixtas entero-flotante
            ('entero', '+', 'flotante'): 'flotante',
            ('entero', '-', 'flotante'): 'flotante',
            ('entero', '*', 'flotante'): 'flotante',
            ('entero', '/', 'flotante'): 'flotante',

            ('flotante', '+', 'entero'): 'flotante',
            ('flotante', '-', 'entero'): 'flotante',
            ('flotante', '*', 'entero'): 'flotante',
            ('flotante', '/', 'entero'): 'flotante',

            # Comparaciones
            ('entero', '<', 'entero'): 'bool',
            ('entero', '>', 'entero'): 'bool',
            ('entero', '==', 'entero'): 'bool',
            ('entero', '!=', 'entero'): 'bool',

            ('flotante', '<', 'flotante'): 'bool',
            ('flotante', '>', 'flotante'): 'bool',
            ('flotante', '==', 'flotante'): 'bool',
            ('flotante', '!=', 'flotante'): 'bool',

            ('entero', '<', 'flotante'): 'bool',
            ('entero', '>', 'flotante'): 'bool',
            ('entero', '==', 'flotante'): 'bool',
            ('entero', '!=', 'flotante'): 'bool',

            ('flotante', '<', 'entero'): 'bool',
            ('flotante', '>', 'entero'): 'bool',
            ('flotante', '==', 'entero'): 'bool',
            ('flotante', '!=', 'entero'): 'bool',

            # Asignaciones
            ('entero', '=', 'entero'): 'entero',
            ('flotante', '=', 'flotante'): 'flotante',
            ('flotante', '=', 'entero'): 'flotante',
        }

    def get_result_type(self, left_type, operator, right_type):
        """
        Regresa el tipo resultante de una operación.

        Ejemplo:
        entero + flotante -> flotante
        entero < flotante -> bool
        entero = flotante -> None
        """
        return self.cube.get((left_type, operator, right_type))

    def is_valid_operation(self, left_type, operator, right_type):
        """
        Regresa True si la operación es válida.
        """
        return self.get_result_type(left_type, operator, right_type) is not None