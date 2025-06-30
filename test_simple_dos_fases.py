import requests
import json

def test_simple_dos_fases():
    """Prueba con un problema simple que definitivamente tiene solución."""
    url = "http://localhost:8003/solve"
    
    # Problema simple de minimización:
    # Minimizar Z = x1 + x2
    # s.a: x1 + x2 >= 1
    #      x1, x2 >= 0
    # Solución óptima: x1=1, x2=0 (o x1=0, x2=1) con Z=1
    
    payload = {
        "method": "dosfases",
        "n_vars": 2,
        "n_cons": 1,
        "c": [1, 1],
        "A": [[1, 1]],
        "b": [1],
        "signs": [">="],
        "obj_type": "min"
    }
    
    print("=== Probando Dos Fases con problema simple ===")
    print("Payload:", json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Respuesta:")
            print(json.dumps(data, indent=2))
        else:
            print("Error:")
            print(response.text)
    except Exception as e:
        print(f"Error en la solicitud: {e}")

if __name__ == "__main__":
    test_simple_dos_fases()
