import requests
import json

def test_gran_m_problema_imagen():
    """Prueba si Gran M puede resolver el problema de la imagen."""
    url = "http://localhost:8003/solve"
    
    payload = {
        "method": "granm",
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    print("=== PROBANDO GRAN M CON EL PROBLEMA DE LA IMAGEN ===")
    print("Si Gran M funciona, entonces Dos Fases debería funcionar también")
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
                print(f"ERROR en Gran M: {data['error']}")
                print("¡Esto sugiere que el problema puede ser fundamental!")
            else:
                print("ÉXITO - Gran M resolvió el problema:")
                if 'solucion_final' in data:
                    print(f"Solución: {data['solucion_final']}")
                if 'valor_objetivo_final' in data:
                    print(f"Valor objetivo: {data['valor_objetivo_final']}")
                print()
                print("Esto confirma que el problema SÍ tiene solución.")
                print("Por tanto, el error está en el método de Dos Fases.")
        else:
            print("Error HTTP:")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gran_m_problema_imagen()
