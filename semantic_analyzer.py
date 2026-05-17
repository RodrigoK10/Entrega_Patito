from semantic_cube import SemanticCube
from function_directory import FunctionDirectory


class SemanticAnalyzer:
    """
    Analizador semántico para Patito.
    """

    def __init__(self):
        self.semantic_cube = SemanticCube()
        self.function_directory = FunctionDirectory()
        self.current_scope = "global"

    def set_current_scope(self, scope_name):
        """
        Cambia el scope actual.
        """
        if not self.function_directory.function_exists(scope_name):
            raise Exception(
                f"Error semántico: el scope '{scope_name}' no existe."
            )

        self.current_scope = scope_name

    def declare_global_variable(self, name, var_type):
        """
        Declara una variable global.
        """
        self.function_directory.add_global_variable(name, var_type)

    def declare_function(self, name, return_type):
        """
        Declara una función y cambia el scope actual a esa función.
        """
        self.function_directory.add_function(name, return_type)
        self.current_scope = name

    def declare_parameter(self, name, param_type):
        """
        Declara un parámetro dentro de la función actual.
        """
        if self.current_scope == "global":
            raise Exception(
                "Error semántico: no se pueden declarar parámetros en el scope global."
            )

        self.function_directory.add_parameter(
            self.current_scope,
            name,
            param_type
        )

    def declare_local_variable(self, name, var_type):
        """
        Declara una variable local dentro del scope actual.
        """
        if self.current_scope == "global":
            self.declare_global_variable(name, var_type)
        else:
            self.function_directory.add_local_variable(
                self.current_scope,
                name,
                var_type
            )

    def validate_variable_usage(self, name):
        """
        Valida que una variable exista antes de usarse.
        """
        return self.function_directory.get_variable_type(
            name,
            self.current_scope
        )

    def validate_operation(self, left_type, operator, right_type):
        """
        Valida una operación entre dos tipos.
        """
        result_type = self.semantic_cube.get_result_type(
            left_type,
            operator,
            right_type
        )

        if result_type is None:
            raise Exception(
                f"Error semántico: operación inválida '{left_type} {operator} {right_type}'."
            )

        return result_type

    def validate_assignment(self, variable_name, expression_type):
        """
        Valida una asignación.
        """
        variable_type = self.validate_variable_usage(variable_name)

        result_type = self.semantic_cube.get_result_type(
            variable_type,
            '=',
            expression_type
        )

        if result_type is None:
            raise Exception(
                f"Error semántico: no se puede asignar un valor de tipo '{expression_type}' "
                f"a la variable '{variable_name}' de tipo '{variable_type}'."
            )

        return result_type

    def validate_condition_expression(self, expression_type):
        """
        Valida que una condición sea booleana.
        """
        if expression_type != "bool":
            raise Exception(
                f"Error semántico: la condición debe ser de tipo 'bool', no '{expression_type}'."
            )

    def print_semantic_structures(self):
        """
        Imprime las estructuras semánticas generadas.
        """
        self.function_directory.print_directory()