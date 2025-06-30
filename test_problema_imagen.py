import requests
import json

def test_problema_imagen():
    """Prueba exactamente el problema que aparece en la imagen del frontend."""
    url = "http://localhost:8003/solve"
    
    # Problema tal como aparece en la imagen:
    # Minimizar Z = 2000x1 + 500x2
    # Restricciones: 2x1 + 3x2 >= 36, 3x1 + 6x2 >= 60
    
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"  # Minimización como muestra la imagen
    }
    
    print("=== Problema exacto de la imagen ===")
    print("Minimizar Z = 2000x1 + 500x2")
    print("Restricciones:")
    print("  2x1 + 3x2 >= 36")
    print("  3x1 + 6x2 >= 60")
    print("  x1, x2 >= 0")
    print()
    
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
                if 'error' in data:
                    print(f"ERROR: {data['error']}")
                else:
                    print("ÉXITO - Solución encontrada:")
                    # Mostrar solo la información clave
                    if method == "granm":
                        if 'solucion_final' in data:
                            print(f"Solución: {data['solucion_final']}")
                        if 'valor_objetivo_final' in data:
                            print(f"Valor objetivo: {data['valor_objetivo_final']}")
                    else:  # dosfases
                        if 'fase2' in data and 'solucion' in data['fase2']:
                            print(f"Solución: {data['fase2']['solucion']}")
                        if 'fase2' in data and 'valor_objetivo' in data['fase2']:
                            print(f"Valor objetivo: {data['fase2']['valor_objetivo']}")
            else:
                print("Error HTTP:")
                print(response.text)
        except Exception as e:
            print(f"Error en la solicitud: {e}")

if __name__ == "__main__":
    test_problema_imagen()
