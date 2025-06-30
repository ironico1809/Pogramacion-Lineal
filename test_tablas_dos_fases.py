import requests
import json

def test_dos_fases_tablas():
    """Probar Dos Fases y ver las tablas completas"""
    
    print("=== PROBANDO DOS FASES - VERIFICANDO TABLAS ===")
    
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
    
    try:
        response = requests.post(
            "http://localhost:8003/solve",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Mostrar estructura completa
            print("\n=== ESTRUCTURA COMPLETA DE RESPUESTA ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verificar si hay tablas
            if 'fase1' in data and 'iteraciones' in data['fase1']:
                print(f"\n✅ Fase 1 tiene {len(data['fase1']['iteraciones'])} iteraciones")
                for i, iter_data in enumerate(data['fase1']['iteraciones']):
                    print(f"   Iteración {i+1}: {list(iter_data.keys())}")
            else:
                print("\n❌ No se encontraron iteraciones en Fase 1")
                
            if 'fase2' in data and 'iteraciones' in data['fase2']:
                print(f"\n✅ Fase 2 tiene {len(data['fase2']['iteraciones'])} iteraciones")
                for i, iter_data in enumerate(data['fase2']['iteraciones']):
                    print(f"   Iteración {i+1}: {list(iter_data.keys())}")
            else:
                print("\n❌ No se encontraron iteraciones en Fase 2")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dos_fases_tablas()
