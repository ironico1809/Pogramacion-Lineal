#!/usr/bin/env python3
"""
Test que simula exactamente lo que hace la API
"""

import sys
import os
import inspect

# Agregar el path exactamente igual que en la API
print(f"🔍 Directorio actual: {os.getcwd()}")
print(f"🔍 __file__: {__file__}")
print(f"🔍 dirname(__file__): {os.path.dirname(__file__)}")

# El path que usa la API desde src/api/
api_path = os.path.join(os.path.dirname(__file__), 'src', 'api')
component_path = os.path.join(api_path, '..', 'components')
print(f"🔍 Path a components: {os.path.abspath(component_path)}")

sys.path.append(component_path)

try:
    from Metodo2F import SimplexDosFases
    
    print(f"📍 Archivo importado desde: {inspect.getfile(SimplexDosFases)}")
    
    # Simular exactamente la llamada de la API
    sm = SimplexDosFases()
    result = sm.solve_from_data(
        n_vars=2,
        n_cons=2,
        c=[2000, 500],
        A=[[2, 3], [3, 6]],
        b=[36, 60],
        signs=[">=", ">="],
        obj_type="min"
    )
    
    print(f"✅ Resultado: {result}")
    
    # Verificar si hay error
    if "error" in result:
        print(f"❌ ERROR ENCONTRADO: {result['error']}")
    else:
        print("✅ Sin errores encontrados")
    
except Exception as e:
    print(f"❌ Excepción: {e}")
    import traceback
    traceback.print_exc()
