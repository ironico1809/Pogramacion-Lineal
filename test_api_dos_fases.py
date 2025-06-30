#!/usr/bin/env python3
"""
Test completo de la API para verificar ambos métodos: Gran M y Dos Fases
"""

import requests
import json

def test_api_method(method_name, method_type="dosfases"):
    """Probar la API con un método específico"""
    url = "http://localhost:8003/solve"
    
    # Datos del problema que aparece en la imagen
    data = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],  # Función objetivo: 2000x1 + 500x2
        "A": [
            [2, 3],  # 2x1 + 3x2 >= 36
            [3, 6]   # 3x1 + 6x2 >= 60
        ],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min",
        "method": method_type
    }
    
    print(f"🔍 PROBANDO API CON MÉTODO {method_name.upper()}")
    print("=" * 50)
    print(f"📤 Datos enviados:")
    print(json.dumps(data, indent=2))
    print()
    
    try:
        response = requests.post(url, json=data, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verificar si hay error
            if "error" in result:
                print(f"❌ Error en la respuesta: {result['error']}")
                return False
            else:
                print("✅ Respuesta exitosa")
                
                # Mostrar información clave
                if "optimal_solution" in result:
                    print(f"🎯 Solución óptima: {result['optimal_solution']}")
                if "optimal_value" in result:
                    print(f"💰 Valor óptimo: {result['optimal_value']}")
                if "status" in result:
                    print(f"📊 Estado: {result['status']}")
                if "iteraciones" in result:
                    print(f"🔄 Iteraciones: {len(result['iteraciones'])} encontradas")
                    
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor en puerto 8003.")
        print("💡 Para iniciar el servidor ejecuta:")
        print("   python api_final.py")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_both_methods():
    """Probar ambos métodos"""
    print("🧪 TEST COMPLETO DE AMBOS MÉTODOS")
    print("=" * 60)
    print()
    
    # Test Dos Fases
    success_dosfases = test_api_method("Dos Fases", "dosfases")
    print()
    
    # Test Gran M
    success_granm = test_api_method("Gran M", "granm")
    print()
    
    # Resumen
    print("📋 RESUMEN DE RESULTADOS")
    print("=" * 60)
    print(f"Dos Fases: {'✅ EXITOSO' if success_dosfases else '❌ FALLÓ'}")
    print(f"Gran M: {'✅ EXITOSO' if success_granm else '❌ FALLÓ'}")
    
    if success_dosfases and success_granm:
        print("\n🎉 ¡AMBOS MÉTODOS FUNCIONAN CORRECTAMENTE!")
        print("✅ La API soporta tanto Dos Fases como Gran M")
    elif success_dosfases:
        print("\n✅ Dos Fases funciona correctamente")
        print("⚠️ Gran M puede necesitar ajustes")
    elif success_granm:
        print("\n✅ Gran M funciona correctamente")
        print("⚠️ Dos Fases puede necesitar ajustes")
    else:
        print("\n❌ Problemas detectados con ambos métodos")
        print("💡 Verificar que el servidor esté corriendo en puerto 8003")

if __name__ == "__main__":
    test_both_methods()
