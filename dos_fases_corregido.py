from fractions import Fraction
from typing import List, Dict, Any
import copy

def solve_dos_fases_corregido(payload: dict) -> dict:
    """
    Versión corregida del método de dos fases.
    """
    n_vars = payload["n_vars"]
    n_cons = payload["n_cons"]
    c = [Fraction(str(x)) for x in payload["c"]]
    A = [[Fraction(str(x)) for x in row] for row in payload["A"]]
    b = [Fraction(str(x)) for x in payload["b"]]
    signs = payload["signs"]
    sentido = payload["obj_type"].lower()

    # Construcción de variables adicionales
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

    # --- Construcción de la tabla inicial para Fase I ---
    tbl = []
    # Fila objetivo Fase I (minimizar suma de artificiales)
    fila_obj = [Fraction(0)] * (len(var_names) + len(slack) + len(exceso))
    fila_obj += [Fraction(1)] * len(artificial)
    fila_obj.append(Fraction(0))
    tbl.append(fila_obj)
    
    # Filas de restricciones
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

    # Ajustar la fila objetivo de Fase I restando las filas de artificiales en la base
    for i, var in enumerate(base):
        if var.startswith("a"):
            idx = headers.index(var)
            for j in range(len(tbl[0])):
                tbl[0][j] -= tbl[i+1][j]

    iteraciones_fase1 = []
    iteraciones_fase2 = []
    
    # Guardar tabla inicial
    iteraciones_fase1.append({
        "headers": ["Base"] + headers + ["b"],
        "rows": [["W"] + [str(x) for x in tbl[0]]] + [[base[i]] + [str(x) for x in tbl[i+1]] for i in range(len(base))]
    })

    # --- FASE I: Simplex para variables artificiales ---
    paso = 1
    while True:
        # Buscar columna pivote (más positivo en Fase I)
        pivot_col = -1
        max_value = Fraction(0)
        for j, val in enumerate(tbl[0][:-1]):
            if val > max_value:
                max_value = val
                pivot_col = j
        if pivot_col == -1:
            break
        
        # Buscar fila pivote
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
            return {"error": "Problema ilimitado en Fase I", "fase1": {"factible": False, "iteraciones": iteraciones_fase1}, "fase2": {"iteraciones": []}}
        
        # Pivoteo
        div = tbl[pivot_row][pivot_col]
        tbl[pivot_row] = [x/div for x in tbl[pivot_row]]
        for i in range(len(tbl)):
            if i != pivot_row:
                coef = tbl[i][pivot_col]
                tbl[i] = [x - coef*y for x, y in zip(tbl[i], tbl[pivot_row])]
        base[pivot_row-1] = headers[pivot_col]
        paso += 1
        iteraciones_fase1.append({
            "headers": ["Base"] + headers + ["b"],
            "rows": [["W"] + [str(x) for x in tbl[0]]] + [[base[i]] + [str(x) for x in tbl[i+1]] for i in range(len(base))]
        })

    # Comprobación de factibilidad
    obj_fase1 = tbl[0][-1]
    if obj_fase1 != 0:
        return {"error": "El problema es INFACTIBLE (la suma de artificiales no es cero en Fase I)", "fase1": {"factible": False, "iteraciones": iteraciones_fase1}, "fase2": {"iteraciones": []}}

    # --- FASE II: Eliminación de artificiales y optimización de la función objetivo original ---
    cols_keep = [i for i, h in enumerate(headers) if not h.startswith("a")]
    headers2 = [headers[i] for i in cols_keep]
    tbl2 = []
    for row in tbl:
        tbl2.append([row[i] for i in cols_keep] + [row[-1]])
    
    # Nueva base para Fase II
    base2 = []
    for i, bvar in enumerate(base):
        if bvar.startswith("a"):
            # Buscar una variable no artificial que sea básica en esta fila
            found = False
            for j, h in enumerate(headers2):
                # Verificar si h puede ser básica en la fila i+1
                if abs(tbl2[i+1][j]) > 1e-10:  # No es cero
                    # Verificar si es la única no-cero en su columna
                    is_basic = True
                    for k in range(1, len(tbl2)):
                        if k != i+1 and abs(tbl2[k][j]) > 1e-10:
                            is_basic = False
                            break
                    if is_basic and abs(tbl2[i+1][j] - 1) < 1e-10:  # Coeficiente es 1
                        base2.append(h)
                        found = True
                        break
            if not found:
                # Si no se encuentra, usar None o la primera variable no artificial disponible
                base2.append(None)
        else:
            base2.append(bvar)
    
    # Nueva fila objetivo (función original)
    fila_obj2 = []
    for h in headers2:
        if h in var_names:
            coef = c[var_names.index(h)]
            fila_obj2.append(-coef if sentido == "max" else coef)
        else:
            fila_obj2.append(Fraction(0))
    fila_obj2.append(Fraction(0))
    
    # Ajuste R0 eliminando variables básicas presentes en R0
    for i, bvar in enumerate(base2):
        if bvar and bvar in headers2:
            idx = headers2.index(bvar)
            coef_R0 = fila_obj2[idx]
            if coef_R0 != 0:
                for j in range(len(fila_obj2)):
                    fila_obj2[j] -= coef_R0 * tbl2[i+1][j]
    
    tbl2[0] = fila_obj2
    
    # Guardar tabla inicial de Fase II
    iteraciones_fase2.append({
        "headers": ["Base"] + headers2 + ["b"],
        "rows": [["Z"] + [str(x) for x in tbl2[0]]] + [[base2[i]] + [str(x) for x in tbl2[i+1]] for i in range(len(base2))]
    })

    # --- FASE II: Simplex para la función objetivo original ---
    paso = 1
    max_iteraciones = 100  # Límite de seguridad
    while paso <= max_iteraciones:
        # Buscar columna pivote
        pivot_col = -1
        if sentido == "max":
            min_value = Fraction(0)
            for j, val in enumerate(tbl2[0][:-1]):
                if val < min_value:
                    min_value = val
                    pivot_col = j
        else:
            max_value = Fraction(0)
            for j, val in enumerate(tbl2[0][:-1]):
                if val > max_value:
                    max_value = val
                    pivot_col = j
        if pivot_col == -1:
            break
        
        # Buscar fila pivote
        min_ratio = None
        pivot_row = None
        valid_ratios = []  # Para debug
        
        for i in range(1, len(tbl2)):
            col = tbl2[i][pivot_col]
            if col > 0:
                ratio = tbl2[i][-1]/col
                valid_ratios.append((i, ratio, col))
                if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                    min_ratio = ratio
                    pivot_row = i
        
        # Si no hay fila pivote válida, verificar si realmente es ilimitado
        if pivot_row is None:
            # Verificar si hay elementos positivos en la columna
            has_positive = any(tbl2[i][pivot_col] > 0 for i in range(1, len(tbl2)))
            if not has_positive:
                # Si no hay elementos positivos, puede ser que necesitemos revisar la lógica
                # o que el problema realmente sea ilimitado
                return {
                    "error": "Problema ilimitado en Fase II", 
                    "fase1": {"factible": True, "iteraciones": iteraciones_fase1}, 
                    "fase2": {"iteraciones": iteraciones_fase2},
                    "debug_info": {
                        "pivot_col": pivot_col,
                        "column_values": [str(tbl2[i][pivot_col]) for i in range(1, len(tbl2))],
                        "valid_ratios": [(i, str(r), str(c)) for i, r, c in valid_ratios]
                    }
                }
            else:
                return {"error": "Error en selección de fila pivote", "fase1": {"factible": True, "iteraciones": iteraciones_fase1}, "fase2": {"iteraciones": iteraciones_fase2}}
        
        # Pivoteo
        div = tbl2[pivot_row][pivot_col]
        tbl2[pivot_row] = [x/div for x in tbl2[pivot_row]]
        for i in range(len(tbl2)):
            if i != pivot_row:
                coef = tbl2[i][pivot_col]
                tbl2[i] = [x - coef*y for x, y in zip(tbl2[i], tbl2[pivot_row])]
        base2[pivot_row-1] = headers2[pivot_col]
        paso += 1
        iteraciones_fase2.append({
            "headers": ["Base"] + headers2 + ["b"],
            "rows": [["Z"] + [str(x) for x in tbl2[0]]] + [[base2[i]] + [str(x) for x in tbl2[i+1]] for i in range(len(base2))],
            "optima": False
        })

    # Marcar la última iteración como óptima
    if iteraciones_fase2:
        iteraciones_fase2[-1]["optima"] = True

    # Extraer solución final
    solucion = {}
    for i, var in enumerate(base2):
        if var and var in var_names:
            solucion[var] = tbl2[i+1][-1]
    for var in var_names:
        if var not in solucion:
            solucion[var] = Fraction(0)

    valor_objetivo = tbl2[0][-1]
    if sentido == "max":
        valor_objetivo = -valor_objetivo

    return {
        "fase1": {"factible": True, "iteraciones": iteraciones_fase1},
        "fase2": {
            "iteraciones": iteraciones_fase2,
            "solucion": {k: str(v) for k, v in solucion.items()},
            "valor_objetivo": str(valor_objetivo)
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
    
    result = solve_dos_fases_corregido(payload)
    print("Resultado:")
    import json
    print(json.dumps(result, indent=2))
