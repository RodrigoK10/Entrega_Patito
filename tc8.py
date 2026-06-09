from main import compilar_solo, TC8_error
from parser import compilar

print("TC-8: Error esperado — asignar flotante a entero")
try:
    compilar(TC8_error)
except Exception as e:
    print(f"ERROR capturado: {e}")
