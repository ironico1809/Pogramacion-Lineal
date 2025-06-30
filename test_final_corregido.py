import requests
import json

def test_dos_fases_corregido():
    """Prueba el método de Dos Fases corregido con el problema de la imagen."""
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
    
    print("=== PROBANDO DOS FASES CORREGIDO ===")
    print("Problema de la imagen:")
    print("  Minimizar Z = 2000x1 + 500x2")
    print("  2x1 + 3x2 >= 36")
    print("  3x1 + 6x2 >= 60")
    print("  x1, x2 >= 0")
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
                print(f"❌ ERROR: {data['error']}")
                if 'debug_info' in data:
                    print("Información de debug:")
                    print(json.dumps(data['debug_info'], indent=2))
            else:
                print("✅ ÉXITO - Dos Fases funcionó!")
                if 'fase2' in data and 'solucion' in data['fase2']:
                    print(f"📊 Solución: {data['fase2']['solucion']}")
                if 'fase2' in data and 'valor_objetivo' in data['fase2']:
                    print(f"💰 Valor objetivo: {data['fase2']['valor_objetivo']}")
                print()
                print("🎉 El problema está resuelto!")
        else:
            print("❌ Error HTTP:")
            print(response.text)
    except Exception as e:
        print(f"❌ Error en la solicitud: {e}")

def test_ambos_metodos():
    """Compara ambos métodos con el problema corregido."""
    url = "http://localhost:8003/solve"
    
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    print("\n" + "="*50)
    print("COMPARACIÓN DE MÉTODOS")
    print("="*50)
    
    for method in ["granm", "dosfases"]:
        payload["method"] = method
        print(f"\n🔬 Método: {method.upper()}")
        
        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print(f"   ❌ Error: {data['error']}")
                else:
                    print("   ✅ Éxito")
                    # Extraer valor objetivo según el método
                    if method == "granm":
                        if 'valor_objetivo_final' in data:
                            print(f"   💰 Valor objetivo: {data['valor_objetivo_final']}")
                        if 'solucion_final' in data:
                            print(f"   📊 Solución: {data['solucion_final']}")
                    else:  # dosfases
                        if 'fase2' in data and 'valor_objetivo' in data['fase2']:
                            print(f"   💰 Valor objetivo: {data['fase2']['valor_objetivo']}")
                        if 'fase2' in data and 'solucion' in data['fase2']:
                            print(f"   📊 Solución: {data['fase2']['solucion']}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Excepción: {e}")

if __name__ == "__main__":
    test_dos_fases_corregido()
    test_ambos_metodos()
