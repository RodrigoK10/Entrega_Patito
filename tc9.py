from main import TC9_error
from parser import compilar

print("TC-9: Error esperado — variable no declarada")
try:
    compilar(TC9_error)
except Exception as e:
    print(f"ERROR capturado: {e}")
