from semantic_analyzer import SemanticAnalyzer


def main():
    analyzer = SemanticAnalyzer()

    print("=== Prueba 1: Declaración de variables globales ===")
    analyzer.declare_global_variable("x", "entero")
    analyzer.declare_global_variable("y", "entero")
    analyzer.declare_global_variable("promedio", "flotante")

    print("Variables globales declaradas correctamente.")

    print("\n=== Prueba 2: Declaración de función ===")
    analyzer.declare_function("sumar", "entero")
    analyzer.declare_parameter("a", "entero")
    analyzer.declare_parameter("b", "entero")
    analyzer.declare_local_variable("resultado", "entero")

    print("Función sumar declarada correctamente.")

    print("\n=== Prueba 3: Validación de operaciones ===")
    result = analyzer.validate_operation("entero", "+", "entero")
    print(f"entero + entero -> {result}")

    result = analyzer.validate_operation("entero", "+", "flotante")
    print(f"entero + flotante -> {result}")

    result = analyzer.validate_operation("flotante", ">", "entero")
    print(f"flotante > entero -> {result}")

    print("\n=== Prueba 4: Validación de asignaciones ===")
    analyzer.set_current_scope("global")
    analyzer.validate_assignment("x", "entero")
    print("x = entero -> válido")

    analyzer.validate_assignment("promedio", "entero")
    print("promedio = entero -> válido")

    print("\n=== Prueba 5: Error esperado, variable doblemente declarada ===")
    try:
        analyzer.declare_global_variable("x", "entero")
    except Exception as error:
        print(error)

    print("\n=== Prueba 6: Error esperado, asignación inválida ===")
    try:
        analyzer.validate_assignment("x", "flotante")
    except Exception as error:
        print(error)

    print("\n=== Estructuras semánticas generadas ===")
    analyzer.print_semantic_structures()


if __name__ == "__main__":
    main()