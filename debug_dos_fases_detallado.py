"""
Versión modificada del método de Dos Fases con debug para investigar el problema.
"""
from fractions import Fraction
from typing import List, Dict, Any
import copy

def solve_dos_fases_debug(payload: dict) -> dict:
    """
    Versión con debug del método de dos fases.
    """
    print("=== INICIANDO DOS FASES CON DEBUG ===")
    
    n_vars = payload["n_vars"]
    n_cons = payload["n_cons"]
    c = [Fraction(str(x)) for x in payload["c"]]
    A = [[Fraction(str(x)) for x in row] for row in payload["A"]]
    b = [Fraction(str(x)) for x in payload["b"]]
    signs = payload["signs"]
    sentido = payload["obj_type"].lower()

    print(f"Problema: {sentido} {c}")
    print(f"Restricciones: {A}, {b}, {signs}")

    # Construcción de variables adicionales (igual que antes)
    var_names = [f"x{i+1}" for i in range(n_vars)]
    slack, exceso, artificial = [], [], []
    base = []
    for i, sign in enumerate(signs):
        if sign == "<=":
            slack.append(f"s{i+1}")
            base.append(f"s{i+1}")
        elif sign == ">=":
            exceso.append(f"e{i+1}")
            artificial.append(f"a{i+1}")
            base.append(f"a{i+1}")
        elif sign == "=":
            artificial.append(f"a{i+1}")
            base.append(f"a{i+1}")

    headers = var_names + slack + exceso + artificial
    print(f"Headers: {headers}")
    print(f"Base inicial: {base}")

    # Construir tabla Fase I (igual que antes)
    tbl = []
    fila_obj = [Fraction(0)] * (len(var_names) + len(slack) + len(exceso))
    fila_obj += [Fraction(1)] * len(artificial)
    fila_obj.append(Fraction(0))
    tbl.append(fila_obj)
    
    for i in range(n_cons):
        row = list(A[i])
        row += [0]*len(slack)
        row += [0]*len(exceso)
        row += [0]*len(artificial)
        if signs[i] == "<=":
            idx = len(var_names) + slack.index(f"s{i+1}")
            row[idx] = 1
        elif signs[i] == ">=":
            idx_e = len(var_names) + len(slack) + exceso.index(f"e{i+1}")
            idx_a = len(var_names) + len(slack) + len(exceso) + artificial.index(f"a{i+1}")
            row[idx_e] = -1
            row[idx_a] = 1
        elif signs[i] == "=":
            idx_a = len(var_names) + len(slack) + len(exceso) + artificial.index(f"a{i+1}")
            row[idx_a] = 1
        row.append(b[i])
        tbl.append(row)

    # Ajustar fila objetivo Fase I
    for i, var in enumerate(base):
        if var.startswith("a"):
            idx = headers.index(var)
            for j in range(len(tbl[0])):
                tbl[0][j] -= tbl[i+1][j]

    print("\n=== TABLA INICIAL FASE I ===")
    print(f"Headers: {['Base'] + headers + ['b']}")
    print(f"W: {[str(x) for x in tbl[0]]}")
    for i in range(len(base)):
        print(f"{base[i]}: {[str(x) for x in tbl[i+1]]}")

    # Fase I (simplificada para debug)
    iteraciones_fase1 = []
    paso = 1
    while True:
        # Verificar optimalidad
        optimal = True
        for val in tbl[0][:-1]:
            if val > 0:
                optimal = False
                break
        if optimal:
            break
            
        # Encontrar columna pivote (más positivo)
        pivot_col = -1
        max_val = Fraction(0)
        for j, val in enumerate(tbl[0][:-1]):
            if val > max_val:
                max_val = val
                pivot_col = j
        
        if pivot_col == -1:
            break
            
        print(f"\nIteración Fase I {paso}: pivot_col = {pivot_col} (valor = {tbl[0][pivot_col]})")
        
        # Encontrar fila pivote
        min_ratio = None
        pivot_row = None
        for i in range(1, len(tbl)):
            col = tbl[i][pivot_col]
            if col > 0:
                ratio = tbl[i][-1]/col
                if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                    min_ratio = ratio
                    pivot_row = i
        
        if pivot_row is None:
            return {"error": "Problema ilimitado en Fase I"}
            
        print(f"  pivot_row = {pivot_row}, ratio = {min_ratio}")
        
        # Pivoteo
        div = tbl[pivot_row][pivot_col]
        tbl[pivot_row] = [x/div for x in tbl[pivot_row]]
        for i in range(len(tbl)):
            if i != pivot_row:
                coef = tbl[i][pivot_col]
                tbl[i] = [x - coef*y for x, y in zip(tbl[i], tbl[pivot_row])]
        base[pivot_row-1] = headers[pivot_col]
        paso += 1
        
        print(f"  Nueva base: {base}")

    # Verificar factibilidad
    obj_fase1 = tbl[0][-1]
    print(f"\nValor objetivo Fase I: {obj_fase1}")
    if obj_fase1 != 0:
        return {"error": "El problema es INFACTIBLE"}

    print("\n=== TRANSICIÓN A FASE II ===")
    
    # Eliminar columnas artificiales
    cols_keep = [i for i, h in enumerate(headers) if not h.startswith("a")]
    headers2 = [headers[i] for i in cols_keep]
    tbl2 = []
    for row in tbl:
        tbl2.append([row[i] for i in cols_keep] + [row[-1]])
    
    print(f"Headers Fase II: {headers2}")
    
    # Nueva base
    base2 = []
    for i, bvar in enumerate(base):
        if bvar.startswith("a"):
            # Buscar variable básica de reemplazo
            found = False
            for j, h in enumerate(headers2):
                is_col_basic = all(
                    (abs(tbl2[rowi][j]) == (1 if rowi == i+1 else 0))
                    for rowi in range(1, len(tbl2))
                )
                if tbl2[i+1][j] == 1 and is_col_basic:
                    base2.append(h)
                    found = True
                    break
            if not found:
                base2.append(None)
        else:
            base2.append(bvar)
    
    print(f"Base Fase II: {base2}")
    
    # Nueva fila objetivo
    fila_obj2 = []
    for h in headers2:
        if h in var_names:
            coef = c[var_names.index(h)]
            fila_obj2.append(-coef if sentido == "max" else coef)
        else:
            fila_obj2.append(Fraction(0))
    fila_obj2.append(Fraction(0))
    
    print(f"Fila objetivo inicial Fase II: {[str(x) for x in fila_obj2]}")
    
    # Ajustar fila objetivo
    for i, bvar in enumerate(base2):
        if bvar and bvar in headers2:
            idx = headers2.index(bvar)
            coef_R0 = fila_obj2[idx]
            if coef_R0 != 0:
                print(f"Ajustando por variable básica {bvar} (coef = {coef_R0})")
                for j in range(len(fila_obj2)):
                    fila_obj2[j] -= coef_R0 * tbl2[i+1][j]
    
    tbl2[0] = fila_obj2
    
    print(f"Fila objetivo ajustada Fase II: {[str(x) for x in fila_obj2]}")
    
    print("\n=== TABLA INICIAL FASE II ===")
    print(f"Headers: {['Base'] + headers2 + ['b']}")
    print(f"Z: {[str(x) for x in tbl2[0]]}")
    for i in range(len(base2)):
        print(f"{base2[i]}: {[str(x) for x in tbl2[i+1]]}")
    
    # Fase II - Primera iteración con debug
    paso = 1
    print(f"\n=== ITERACIÓN FASE II {paso} ===")
    
    # Buscar columna pivote
    pivot_col = -1
    if sentido == "max":
        min_value = Fraction(0)
        for j, val in enumerate(tbl2[0][:-1]):
            if val < min_value:
                min_value = val
                pivot_col = j
    else:  # minimización
        max_value = Fraction(0)
        for j, val in enumerate(tbl2[0][:-1]):
            if val > max_value:
                max_value = val
                pivot_col = j
    
    if pivot_col == -1:
        print("Ya es óptimo")
        return {"success": "Solución encontrada (ya óptimo)"}
    
    print(f"Columna pivote: {pivot_col} (valor = {tbl2[0][pivot_col]})")
    print(f"Columna pivote corresponde a variable: {headers2[pivot_col]}")
    
    # Mostrar toda la columna pivote
    print("Valores en la columna pivote:")
    for i in range(1, len(tbl2)):
        print(f"  Fila {i} ({base2[i-1]}): {tbl2[i][pivot_col]}")
    
    # Buscar fila pivote
    min_ratio = None
    pivot_row = None
    print("Calculando ratios:")
    for i in range(1, len(tbl2)):
        col = tbl2[i][pivot_col]
        print(f"  Fila {i}: col = {col}, b = {tbl2[i][-1]}")
        if col > 0:
            ratio = tbl2[i][-1]/col
            print(f"    Ratio = {ratio}")
            if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                min_ratio = ratio
                pivot_row = i
                print(f"    Nuevo mínimo ratio!")
        else:
            print(f"    col <= 0, no válido para ratio")
    
    if pivot_row is None:
        print("ERROR: No se encontró fila pivote válida")
        print("Esto indica que el problema es ilimitado")
        return {"error": "Problema ilimitado en Fase II (debug)"}
    else:
        print(f"Fila pivote seleccionada: {pivot_row} (ratio = {min_ratio})")
        return {"success": "Debug completado - se encontró fila pivote válida"}

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
    
    result = solve_dos_fases_debug(payload)
    print(f"\nResultado final: {result}")
