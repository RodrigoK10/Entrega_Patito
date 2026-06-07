from parser import compilar
from virtual_machine import VirtualMachine

# ─────────────────────────────────────────────────────────────────────────────
# Utilidades
# ─────────────────────────────────────────────────────────────────────────────

def correr(codigo, titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)
    fd, quads, mem = compilar(codigo)
    quads.desplegar()
    print("\n--- Ejecución ---")
    vm = VirtualMachine(fd, quads, mem)
    vm.ejecutar()


def compilar_solo(codigo, titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)
    fd, quads, mem = compilar(codigo)
    quads.desplegar()
    fd.print_directory()


# ─────────────────────────────────────────────────────────────────────────────
# TC-1: Hola mundo (imprime string y expresión entera)
# ─────────────────────────────────────────────────────────────────────────────
TC1 = """
programa tc1;
principal ()
{
    imprime("Hola Patito");
    imprime(3 + 4);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-2: Variables globales y asignación
# ─────────────────────────────────────────────────────────────────────────────
TC2 = """
programa tc2;
vars {
    entero x, y, suma;
    flotante promedio;
}
principal ()
{
    x = 10;
    y = 20;
    suma = x + y;
    promedio = suma / 2;
    imprime("Suma:");
    imprime(suma);
    imprime("Promedio:");
    imprime(promedio);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-3: Condicional si / sino
# ─────────────────────────────────────────────────────────────────────────────
TC3 = """
programa tc3;
vars {
    entero n;
}
principal ()
{
    n = 7;
    si (n > 5) entonces
    {
        imprime("Mayor que 5");
    }
    sino
    {
        imprime("Menor o igual a 5");
    }
    fin_si
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-4: Ciclo mientras
# ─────────────────────────────────────────────────────────────────────────────
TC4 = """
programa tc4;
vars {
    entero i, acum;
}
principal ()
{
    i = 1;
    acum = 0;
    mientras (i < 6) haz
    {
        acum = acum + i;
        i = i + 1;
    }
    fin_mientras
    imprime("Suma 1..5:");
    imprime(acum);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-5: Declaración e invocación de función (cuádruplos ERA/PARAM/GOSUB)
# ─────────────────────────────────────────────────────────────────────────────
TC5 = """
programa tc5;
vars {
    entero resultado;
}

funcion sumar (a : entero, b : entero)
{
    imprime(a + b);
}

principal ()
{
    sumar(3, 4);
    resultado = 10;
    sumar(resultado, 5);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-6: Función con variable local y ciclo interno
# ─────────────────────────────────────────────────────────────────────────────
TC6 = """
programa tc6;

funcion tabla (n : entero)
vars {
    entero i;
}
{
    i = 1;
    mientras (i < 11) haz
    {
        imprime(n * i);
        i = i + 1;
    }
    fin_mientras
}

principal ()
{
    imprime("Tabla del 3:");
    tabla(3);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-7: Dos funciones, condicional anidado
# ─────────────────────────────────────────────────────────────────────────────
TC7 = """
programa tc7;
vars {
    entero a, b;
}

funcion maximo (x : entero, y : entero)
{
    si (x > y) entonces
    {
        imprime(x);
    }
    sino
    {
        imprime(y);
    }
    fin_si
}

funcion minimo (x : entero, y : entero)
{
    si (x < y) entonces
    {
        imprime(x);
    }
    sino
    {
        imprime(y);
    }
    fin_si
}

principal ()
{
    a = 8;
    b = 13;
    imprime("Max:");
    maximo(a, b);
    imprime("Min:");
    minimo(a, b);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-8: Error semántico esperado (tipo incompatible)
# ─────────────────────────────────────────────────────────────────────────────
TC8_error = """
programa tc8;
vars {
    entero x;
    flotante y;
}
principal ()
{
    x = y;
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# TC-9: Error semántico esperado (variable no declarada)
# ─────────────────────────────────────────────────────────────────────────────
TC9_error = """
programa tc9;
principal ()
{
    imprime(z);
}
fin
"""

# ─────────────────────────────────────────────────────────────────────────────
# Ejecución
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    correr(TC1, "TC-1: Hola mundo")
    correr(TC2, "TC-2: Variables globales y aritmética")
    correr(TC3, "TC-3: Condicional si/sino")
    correr(TC4, "TC-4: Ciclo mientras (suma 1..5)")
    correr(TC5, "TC-5: Declaración e invocación de función")
    correr(TC6, "TC-6: Función con variable local y ciclo")
    correr(TC7, "TC-7: Dos funciones, maximo/minimo")

    print(f"\n{'='*60}")
    print("  TC-8: Error esperado — asignar flotante a entero")
    print('='*60)
    try:
        compilar(TC8_error)
    except Exception as e:
        print(f"ERROR capturado: {e}")

    print(f"\n{'='*60}")
    print("  TC-9: Error esperado — variable no declarada")
    print('='*60)
    try:
        compilar(TC9_error)
    except Exception as e:
        print(f"ERROR capturado: {e}")
