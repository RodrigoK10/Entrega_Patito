from symbol_table import VariableTable


class FunctionInfo:
    """
    Representa la información semántica de una función.
    """

    def __init__(self, name, return_type):
        self.name = name
        self.return_type = return_type
        self.parameters = []
        self.variable_table = VariableTable(scope_name=name)
        self.inicio = None
        self.tam_local_entero = 0
        self.tam_local_flotante = 0
        self.tam_local_bool = 0

    def add_parameter(self, param_name, param_type):
        """
        Agrega un parámetro a la función.
        """
        self.parameters.append({
            "name": param_name,
            "type": param_type
        })

        self.variable_table.add_variable(
            name=param_name,
            var_type=param_type
        )

    def add_local_variable(self, var_name, var_type):
        """
        Agrega una variable local a la función.
        """
        self.variable_table.add_variable(
            name=var_name,
            var_type=var_type
        )

    def to_dict(self):
        return {
            "name": self.name,
            "return_type": self.return_type,
            "parameters": self.parameters,
            "variables": self.variable_table.to_dict(),
            "inicio": self.inicio,
            "tam_local_entero": self.tam_local_entero,
            "tam_local_flotante": self.tam_local_flotante,
            "tam_local_bool": self.tam_local_bool
        }


class FunctionDirectory:
    """
    Directorio de funciones para Patito.
    """

    def __init__(self):
        self.functions = {}

        # Scope global del programa
        self.functions["global"] = FunctionInfo(
            name="global",
            return_type="nula"
        )

    def add_function(self, name, return_type):
        """
        Agrega una función al directorio.
        """
        if name in self.functions:
            raise Exception(
                f"Error semántico: la función '{name}' ya fue declarada."
            )

        self.functions[name] = FunctionInfo(
            name=name,
            return_type=return_type
        )

    def function_exists(self, name):
        """
        Verifica si una función existe.
        """
        return name in self.functions

    def get_function(self, name):
        """
        Obtiene la información de una función.
        """
        if name not in self.functions:
            raise Exception(
                f"Error semántico: la función '{name}' no ha sido declarada."
            )

        return self.functions[name]

    def set_inicio(self, name, numero_cuadruplo):
        """
        Registra el número del primer cuádruplo de la función.
        """
        self.get_function(name).inicio = numero_cuadruplo

    def add_global_variable(self, var_name, var_type):
        """
        Agrega una variable global.
        """
        self.functions["global"].variable_table.add_variable(
            name=var_name,
            var_type=var_type
        )

    def add_local_variable(self, function_name, var_name, var_type):
        """
        Agrega una variable local a una función específica.
        """
        function = self.get_function(function_name)
        function.add_local_variable(var_name, var_type)

    def add_parameter(self, function_name, param_name, param_type):
        """
        Agrega un parámetro a una función específica.
        """
        function = self.get_function(function_name)
        function.add_parameter(param_name, param_type)

    def get_variable_type(self, var_name, current_scope):
        """
        Busca el tipo de una variable.
        """
        if current_scope in self.functions:
            local_table = self.functions[current_scope].variable_table

            if local_table.variable_exists(var_name):
                return local_table.get_variable_type(var_name)

        global_table = self.functions["global"].variable_table

        if global_table.variable_exists(var_name):
            return global_table.get_variable_type(var_name)

        raise Exception(
            f"Error semántico: la variable '{var_name}' no ha sido declarada."
        )

    def to_dict(self):
        return {
            name: info.to_dict()
            for name, info in self.functions.items()
        }

    def print_directory(self):
        print("\nDirectorio de Funciones")
        print("=" * 60)

        for function in self.functions.values():
            print(f"\nFunción: {function.name}")
            print(f"Tipo de retorno: {function.return_type}")
            print(f"Inicio: {function.inicio}")
            print(f"Parámetros: {function.parameters}")
            function.variable_table.print_table()