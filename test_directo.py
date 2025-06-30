import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.getcwd())

# Importar la función directamente
try:
    from dosfases_backend import solve_dos_fases_from_payload
    
    # El payload del problema
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    print("=== PROBANDO FUNCIÓN DOS FASES DIRECTAMENTE ===")
    print("Esto nos permitirá ver los mensajes de debug...")
    print()
    
    result = solve_dos_fases_from_payload(payload)
    
    print("\n=== RESULTADO ===")
    import json
    print(json.dumps(result, indent=2))
    
except ImportError as e:
    print(f"Error importando: {e}")
except Exception as e:
    print(f"Error ejecutando: {e}")
    import traceback
    traceback.print_exc()
