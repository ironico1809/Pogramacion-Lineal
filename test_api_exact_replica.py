#!/usr/bin/env python3
"""
Test directo de la funcionalidad de la API sin FastAPI
Para identificar exactamente dónde está el problema
"""

import sys
import os

# Configurar el path exactamente como en la API
current_dir = os.path.dirname(os.path.abspath(__file__))
components_path = os.path.join(current_dir, 'src', 'components')
sys.path.insert(0, components_path)

print(f"🔍 Directorio actual: {current_dir}")
print(f"🔍 Path a components: {components_path}")
print(f"🔍 Existe el directorio? {os.path.exists(components_path)}")

# Listar archivos en components
if os.path.exists(components_path):
    files = os.listdir(components_path)
    metodo2f_files = [f for f in files if 'Metodo2F' in f]
    print(f"🔍 Archivos Metodo2F encontrados: {metodo2f_files}")

try:
    # Importar exactamente como en la API
    from Metodo2F import SimplexDosFases
    import inspect
    
    print(f"✅ Import exitoso")
    print(f"📍 Archivo importado: {inspect.getfile(SimplexDosFases)}")
    
    # Datos de prueba idénticos al frontend
    test_data = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min",
        "method": "dosfases"
    }
    
    print(f"\n🧪 EJECUTANDO TEST CON DATOS DEL FRONTEND:")
    print(f"📤 Datos: {test_data}")
    
    # Ejecutar exactamente la misma lógica que la API
    sm = SimplexDosFases()
    result = sm.solve_from_data(
        n_vars=test_data["n_vars"],
        n_cons=test_data["n_cons"],
        c=test_data["c"],
        A=test_data["A"],
        b=test_data["b"],
        signs=test_data["signs"],
        obj_type=test_data["obj_type"]
    )
    
    print(f"\n📥 RESULTADO:")
    
    # Verificar si hay error
    if "error" in result:
        print(f"❌ ERROR ENCONTRADO: {result['error']}")
        print(f"🔍 Tipo de error: {type(result['error'])}")
        
        # Buscar de dónde viene este error
        if "específico del usuario" in result["error"]:
            print(f"🚨 ESTE ES EL ERROR QUE CAUSA PROBLEMAS EN EL FRONTEND")
            
            # Verificar si el error viene del resultado o de otro lado
            print(f"🔍 Contenido completo del resultado:")
            for key, value in result.items():
                print(f"   {key}: {value}")
    else:
        print(f"✅ SIN ERRORES - Funcionamiento correcto")
        
        # Mostrar resumen
        fase1 = result.get("fase1", {})
        fase2 = result.get("fase2", {})
        
        print(f"📊 Resumen:")
        print(f"   Fase I factible: {fase1.get('factible', 'N/A')}")
        print(f"   Fase I iteraciones: {len(fase1.get('iteraciones', []))}")
        print(f"   Fase II iteraciones: {len(fase2.get('iteraciones', []))}")
        
        if fase2.get('ilimitado'):
            print(f"   Resultado: Problema ilimitado")
        else:
            print(f"   Resultado: Revisar iteraciones")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print(f"🔍 Archivos disponibles en components:")
    if os.path.exists(components_path):
        for file in os.listdir(components_path):
            print(f"   - {file}")
            
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
