import requests
import json

def test_debug_paso_a_paso():
    """Prueba el problema con debug detallado."""
    url = "http://localhost:8003/solve"
    
    # El problema exacto de la imagen
    payload = {
        "method": "dosfases",
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    print("=== DEBUG DETALLADO - DOS FASES ===")
    print("Problema:")
    print("  Minimizar Z = 2000x1 + 500x2")
    print("  2x1 + 3x2 >= 36")
    print("  3x1 + 6x2 >= 60")
    print("  x1, x2 >= 0")
    print()
    print("Análisis teórico:")
    print("  - Este problema DEBE tener solución óptima finita")
    print("  - La región factible está bien definida")
    print("  - No debería ser ilimitado")
    print()
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Respuesta completa:")
            print(json.dumps(data, indent=2))
        else:
            print("Error HTTP:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

def test_problema_simple_factible():
    """Prueba con un problema que definitivamente tiene solución."""
    url = "http://localhost:8003/solve"
    
    # Problema muy simple que definitivamente tiene solución
    # Minimizar Z = x1 + x2
    # x1 + x2 >= 2
    # Solución óptima: x1=2, x2=0 (o x1=0, x2=2, o cualquier combinación), Z=2
    
    payload = {
        "method": "dosfases",
        "n_vars": 2,
        "n_cons": 1,
        "c": [1, 1],
        "A": [[1, 1]],
        "b": [2],
        "signs": [">="],
        "obj_type": "min"
    }
    
    print("\n=== PROBLEMA SIMPLE PARA VERIFICAR DOS FASES ===")
    print("Minimizar Z = x1 + x2")
    print("x1 + x2 >= 2")
    print("x1, x2 >= 0")
    print("Solución esperada: x1=2, x2=0 (o similar), Z=2")
    print()
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"ERROR: {data['error']}")
                print("¡Esto confirma que hay un bug en el método de Dos Fases!")
            else:
                print("ÉXITO - El método de Dos Fases funciona")
                print("Respuesta:")
                print(json.dumps(data, indent=2))
        else:
            print("Error HTTP:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_debug_paso_a_paso()
    test_problema_simple_factible()
