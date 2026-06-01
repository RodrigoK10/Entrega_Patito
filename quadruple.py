# quadruple.py - Cuádruplos para Patito

class Cuadruplo:
    def __init__(self, numero, operador, izquierdo, derecho, resultado):
        self.numero = numero
        self.operador = operador
        self.izquierdo = izquierdo
        self.derecho = derecho
        self.resultado = resultado

    def __repr__(self):
        return (f"[{self.numero:>3}] {str(self.operador):<8} "
                f"{str(self.izquierdo):<10} {str(self.derecho):<10} {str(self.resultado)}")


class FilaCuadruplos:
    def __init__(self):
        self._fila = []

    def agregar(self, operador, izquierdo, derecho, resultado):
        n = len(self._fila)
        self._fila.append(Cuadruplo(n, operador, izquierdo, derecho, resultado))
        return n

    def get(self, n):
        return self._fila[n]

    def rellena_salto(self, n, destino):
        self._fila[n].resultado = destino

    def siguiente(self):
        return len(self._fila)

    def desplegar(self):
        print("\n=== Cuádruplos ===")
        for q in self._fila:
            print(q)