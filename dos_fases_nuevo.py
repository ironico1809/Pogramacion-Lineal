from fractions import Fraction
from typing import List, Dict, Any
import copy

def solve_dos_fases_nuevo(payload: dict) -> dict:
    """
    Implementación completamente nueva del método de dos fases
    que maneja correctamente problemas con restricciones >=.
    """
    n_vars = payload["n_vars"]
    n_cons = payload["n_cons"]
    c = [Fraction(str(x)) for x in payload["c"]]
    A = [[Fraction(str(x)) for x in row] for row in payload["A"]]
    b = [Fraction(str(x)) for x in payload["b"]]
    signs = payload["signs"]
    sentido = payload["obj_type"].lower()

    print(f"=== INICIANDO DOS FASES NUEVO ===")
    print(f"Problema: {sentido}")
    print(f"c = {c}")
    print(f"A = {A}")
    print(f"b = {b}")
    print(f"signs = {signs}")

    # Construcción de variables
    var_names = [f"x{i+1}" for i in range(n_vars)]
    slack = []
    artificial = []
    base = []
    
    # Para restricciones >=, no usaremos variables de exceso problemáticas
    # En su lugar, convertiremos a <= multiplicando por -1
    A_modified = []
    b_modified = []
    signs_modified = []
    
    for i, sign in enumerate(signs):
        if sign == "<=":
            A_modified.append(A[i])
            b_modified.append(b[i])
            signs_modified.append("<=")
            slack.append(f"s{len(slack)+1}")
            base.append(f"s{len(slack)}")
        elif sign == ">=":
            # Convertir >= a <= multiplicando por -1
            A_modified.append([-x for x in A[i]])
            b_modified.append(-b[i])
            signs_modified.append("<=")
            slack.append(f"s{len(slack)+1}")
            base.append(f"s{len(slack)}")
        elif sign == "=":
            A_modified.append(A[i])
            b_modified.append(b[i])
            signs_modified.append("=")
            artificial.append(f"a{len(artificial)+1}")
            base.append(f"a{len(artificial)}")

    print(f"A_modified = {A_modified}")
    print(f"b_modified = {b_modified}")
    print(f"signs_modified = {signs_modified}")
    print(f"Variables slack: {slack}")
    print(f"Variables artificial: {artificial}")
    print(f"Base inicial: {base}")

    # Verificar si todas las b_modified son no negativas
    for i, val in enumerate(b_modified):
        if val < 0:
            print(f"ERROR: b_modified[{i}] = {val} < 0")
            print("Necesitamos agregar variables artificiales para valores negativos")
            # Para valores negativos de b, necesitamos variables artificiales
            artificial.append(f"a{len(artificial)+1}")
            base[i] = f"a{len(artificial)}"

    headers = var_names + slack + artificial

    # Solo necesitamos Fase I si hay variables artificiales
    if not artificial:
        print("No hay variables artificiales - ir directamente a optimización")
        # Ir directamente a la optimización (sin Fase I)
        return {"error": "Implementación directa no disponible aún"}

    # --- CONSTRUCCIÓN TABLA FASE I ---
    print(f"\n=== TABLA FASE I ===")
    print(f"Headers: {headers}")
    
    # Fila objetivo Fase I: minimizar suma de artificiales
    fila_obj = [Fraction(0)] * len(var_names)  # x1, x2, ...
    fila_obj += [Fraction(0)] * len(slack)     # s1, s2, ...
    fila_obj += [Fraction(1)] * len(artificial)  # a1, a2, ...
    fila_obj.append(Fraction(0))  # término independiente
    
    tbl = [fila_obj]
    
    # Filas de restricciones
    for i in range(n_cons):
        row = list(A_modified[i])  # Coeficientes de x1, x2, ...
        
        # Agregar coeficientes de variables slack
        for j in range(len(slack)):
            if signs_modified[i] == "<=" and j == i:
                row.append(Fraction(1))
            else:
                row.append(Fraction(0))
        
        # Agregar coeficientes de variables artificiales
        for j in range(len(artificial)):
            if f"a{j+1}" == base[i]:
                row.append(Fraction(1))
            else:
                row.append(Fraction(0))
        
        row.append(b_modified[i])  # término independiente
        tbl.append(row)
    
    print("Tabla inicial (antes de ajustar):")
    print("Headers:", ["Base"] + headers + ["b"])
    print("W:", [str(x) for x in tbl[0]])
    for i in range(len(base)):
        print(f"{base[i]}:", [str(x) for x in tbl[i+1]])
    
    # Ajustar fila objetivo eliminando artificiales básicas
    for i, var in enumerate(base):
        if var.startswith("a"):
            print(f"Ajustando por variable artificial {var}")
            for j in range(len(tbl[0])):
                tbl[0][j] -= tbl[i+1][j]
    
    print("\nTabla ajustada:")
    print("W:", [str(x) for x in tbl[0]])
    for i in range(len(base)):
        print(f"{base[i]}:", [str(x) for x in tbl[i+1]])

    # Aplicar Simplex en Fase I
    iteraciones_fase1 = []
    iteraciones_fase1.append({
        "headers": ["Base"] + headers + ["b"],
        "rows": [["W"] + [str(x) for x in tbl[0]]] + [[base[i]] + [str(x) for x in tbl[i+1]] for i in range(len(base))]
    })
    
    paso = 1
    max_iter = 50
    while paso <= max_iter:
        print(f"\n--- Iteración Fase I {paso} ---")
        
        # Buscar columna pivote (más negativo para minimización en Fase I)
        pivot_col = -1
        min_val = Fraction(0)
        for j, val in enumerate(tbl[0][:-1]):
            if val < min_val:
                min_val = val
                pivot_col = j
        
        if pivot_col == -1:
            print("Óptimo alcanzado en Fase I")
            break
        
        print(f"Columna pivote: {pivot_col} ({headers[pivot_col]}) = {tbl[0][pivot_col]}")
        
        # Buscar fila pivote
        min_ratio = None
        pivot_row = None
        print("Calculando ratios:")
        for i in range(1, len(tbl)):
            col_val = tbl[i][pivot_col]
            b_val = tbl[i][-1]
            print(f"  Fila {i} ({base[i-1]}): {b_val}/{col_val}", end="")
            if col_val > 0:
                ratio = b_val / col_val
                print(f" = {ratio}")
                if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                    min_ratio = ratio
                    pivot_row = i
            else:
                print(" (no válido)")
        
        if pivot_row is None:
            return {"error": "Problema ilimitado en Fase I"}
        
        print(f"Fila pivote: {pivot_row} (ratio = {min_ratio})")
        
        # Realizar pivoteo
        pivot_element = tbl[pivot_row][pivot_col]
        print(f"Elemento pivote: {pivot_element}")
        
        # Normalizar fila pivote
        for j in range(len(tbl[pivot_row])):
            tbl[pivot_row][j] /= pivot_element
        
        # Eliminar columna pivote en otras filas
        for i in range(len(tbl)):
            if i != pivot_row:
                multiplier = tbl[i][pivot_col]
                for j in range(len(tbl[i])):
                    tbl[i][j] -= multiplier * tbl[pivot_row][j]
        
        # Actualizar base
        base[pivot_row-1] = headers[pivot_col]
        
        print(f"Nueva base: {base}")
        print("Nueva tabla:")
        for i in range(len(tbl)):
            if i == 0:
                print("W:", [str(x) for x in tbl[i]])
            else:
                print(f"{base[i-1]}:", [str(x) for x in tbl[i]])
        
        iteraciones_fase1.append({
            "headers": ["Base"] + headers + ["b"],
            "rows": [["W"] + [str(x) for x in tbl[0]]] + [[base[i]] + [str(x) for x in tbl[i+1]] for i in range(len(base))]
        })
        
        paso += 1

    # Verificar factibilidad
    obj_fase1 = tbl[0][-1]
    print(f"\nValor objetivo Fase I: {obj_fase1}")
    if abs(float(obj_fase1)) > 1e-10:
        return {"error": f"Problema infactible - Fase I terminó con valor {obj_fase1}"}

    print("\n=== FASE I COMPLETADA EXITOSAMENTE ===")
    return {
        "fase1": {
            "factible": True,
            "iteraciones": iteraciones_fase1
        },
        "fase2": {
            "iteraciones": [],
            "mensaje": "Fase II pendiente de implementar"
        }
    }

# Test
if __name__ == "__main__":
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]],
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    result = solve_dos_fases_nuevo(payload)
    print("\n=== RESULTADO ===")
    import json
    print(json.dumps(result, indent=2))
