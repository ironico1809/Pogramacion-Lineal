import requests
import json

def test_backend():
    """Prueba el backend directamente"""
    print("=== PRUEBA BACKEND ===")
    
    # Datos de prueba
    payload = {
        "method": "granm",
        "n_vars": 2,
        "n_cons": 2,
        "c": [1, 1],
        "A": [[1, 1], [1, 1]],
        "b": [1, 1],
        "signs": ["<=", "<="],
        "obj_type": "min"
    }
    
    try:
        print("Enviando solicitud a http://localhost:8000/solve")
        print("Payload:", json.dumps(payload, indent=2))
        
        response = requests.post(
            "http://localhost:8000/solve",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Respuesta exitosa:")
            print(json.dumps(data, indent=2))
        else:
            print("Error:")
            print(response.text)
            
    except Exception as e:
        print(f"Error en la solicitud: {e}")

if __name__ == "__main__":
    test_backend()
