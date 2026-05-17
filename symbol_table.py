class VariableInfo:
    """
    Representa la información semántica de una variable.
    """

    def __init__(self, name, var_type, scope, address=None):
        self.name = name
        self.var_type = var_type
        self.scope = scope
        self.address = address

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.var_type,
            "scope": self.scope,
            "address": self.address
        }


class VariableTable:
    """
    Tabla de variables para un scope específico.
    """

    def __init__(self, scope_name):
        self.scope_name = scope_name
        self.variables = {}

    def add_variable(self, name, var_type, address=None):
        """
        Agrega una variable a la tabla.
        """
        if name in self.variables:
            raise Exception(
                f"Error semántico: la variable '{name}' ya fue declarada en el scope '{self.scope_name}'."
            )

        self.variables[name] = VariableInfo(
            name=name,
            var_type=var_type,
            scope=self.scope_name,
            address=address
        )

    def variable_exists(self, name):
        """
        Verifica si una variable existe en la tabla.
        """
        return name in self.variables

    def get_variable(self, name):
        """
        Obtiene la información de una variable.
        """
        if name not in self.variables:
            raise Exception(
                f"Error semántico: la variable '{name}' no ha sido declarada en el scope '{self.scope_name}'."
            )

        return self.variables[name]

    def get_variable_type(self, name):
        """
        Obtiene el tipo de una variable.
        """
        return self.get_variable(name).var_type

    def to_dict(self):
        return {
            name: info.to_dict()
            for name, info in self.variables.items()
        }

    def print_table(self):
        print(f"\nTabla de Variables, scope: {self.scope_name}")
        print("-" * 60)
        print(f"{'Nombre':<15} {'Tipo':<15} {'Scope':<15} {'Dirección':<15}")
        print("-" * 60)

        for var in self.variables.values():
            print(f"{var.name:<15} {var.var_type:<15} {var.scope:<15} {str(var.address):<15}")