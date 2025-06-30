#!/usr/bin/env python3
"""
Script para probar la API sin usar el servidor uvicorn
Simula exactamente lo que hace el endpoint /solve
"""

import sys
import os

# Agregar el path desde el directorio API
sys.path.append(os.path.join('..', 'components'))

from Metodo2F import SimplexDosFases
from MetodoM_NEW import SimplexTablaInicialCompleta

def simulate_api_call():
    """Simula la llamada a la API"""
    
    # Datos de prueba (igual que en el frontend)
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
    
    print("🔍 SIMULANDO API CALL - MÉTODO DOS FASES")
    print("=" * 60)
    print(f"📤 Datos: {data}")
    print()
    
    try:
        if data["method"] == "dosfases":
            print("🔍 DEBUG: Creando instancia de SimplexDosFases")
            sm = SimplexDosFases()
            print("🔍 DEBUG: Llamando solve_from_data")
            result = sm.solve_from_data(
                n_vars=data["n_vars"],
                n_cons=data["n_cons"],
                c=data["c"],
                A=data["A"],
                b=data["b"],
                signs=data["signs"],
                obj_type=data["obj_type"]
            )
            print(f"🔍 DEBUG: Resultado obtenido")
            print()
            
            # Verificar si hay error
            if "error" in result:
                print(f"❌ ERROR: {result['error']}")
                return False
            else:
                print("✅ ÉXITO - Sin errores")
                
                # Mostrar resumen del resultado
                fase1 = result.get("fase1", {})
                fase2 = result.get("fase2", {})
                
                print(f"📊 FASE I:")
                print(f"   Factible: {fase1.get('factible', 'N/A')}")
                print(f"   Iteraciones: {len(fase1.get('iteraciones', []))}")
                
                print(f"📊 FASE II:")
                fase2_iters = fase2.get('iteraciones', [])
                print(f"   Iteraciones: {len(fase2_iters)}")
                
                if fase2.get('ilimitado'):
                    print(f"   Resultado: Ilimitado")
                elif len(fase2_iters) > 0 and fase2_iters[-1].get('optima'):
                    print(f"   Resultado: Óptimo encontrado")
                else:
                    print(f"   Resultado: En proceso")
                
                return True
                
    except Exception as e:
        print(f"❌ EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_api_call()
    if success:
        print("🎉 ¡La API funcionaría correctamente!")
    else:
        print("❌ La API tendría problemas")
