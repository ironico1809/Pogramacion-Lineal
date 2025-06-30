#!/usr/bin/env python3
"""
Test para la API v2.0 en puerto 8002
"""

import requests
import json
import time

def test_api_v2():
    """Test de la API v2.0"""
    url = "http://localhost:8002/solve"
    
    # Datos de prueba
    data = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min",
        "method": "dosfases"
    }
    
    print("🔍 PROBANDO API v2.0 - PUERTO 8002")
    print("=" * 50)
    
    # Esperar un momento para que la API se inicie
    print("⏳ Esperando que la API se inicie...")
    time.sleep(3)
    
    try:
        # Test de health primero
        health_response = requests.get("http://localhost:8002/health", timeout=5)
        print(f"🏥 Health check: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print(f"✅ API v2.0 está ejecutándose")
        
        # Test principal
        print(f"📤 Enviando datos:")
        print(json.dumps(data, indent=2))
        
        response = requests.post(url, json=data, timeout=10)
        
        print(f"\n📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 Respuesta:")
            print(json.dumps(result, indent=2))
            
            if "error" in result:
                print(f"\n❌ ERROR: {result['error']}")
                
                if "específico del usuario" in result["error"]:
                    print("🚨 MISMO ERROR PERSISTENTE")
                    return False
                else:
                    print("🔍 Error diferente")
                    return False
            else:
                print(f"\n✅ ÉXITO - API v2.0 funciona correctamente")
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar a la API v2.0. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_v2()
    
    if success:
        print("\n🎉 ¡API v2.0 FUNCIONA CORRECTAMENTE!")
        print("El problema del método Dos Fases está resuelto.")
    else:
        print("\n❌ API v2.0 aún tiene problemas.")
        print("El problema persiste y requiere investigación adicional.")
