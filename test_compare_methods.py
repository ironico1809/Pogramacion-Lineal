import requests
import json

def test_compare_methods():
    """Prueba el backend con el mismo problema usando Gran M y Dos Fases y compara las respuestas."""
    url = "http://localhost:8003/solve"
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"  # Cambiado a minimización para que sea consistente con el frontend
    }
    
    for method in ["granm", "dosfases"]:
        payload["method"] = method
        print(f"\n=== Probando método: {method.upper()} ===")
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
    test_compare_methods()
