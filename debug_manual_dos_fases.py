"""
Implementación corregida del método de Dos Fases para debugging.
"""
from fractions import Fraction

def debug_dos_fases(payload):
    """Debug paso a paso del método de Dos Fases."""
    print("=== INICIANDO DEBUG DOS FASES ===")
    
    n_vars = payload["n_vars"]
    n_cons = payload["n_cons"] 
    c = [Fraction(str(x)) for x in payload["c"]]
    A = [[Fraction(str(x)) for x in row] for row in payload["A"]]
    b = [Fraction(str(x)) for x in payload["b"]]
    signs = payload["signs"]
    sentido = payload["obj_type"].lower()
    
    print(f"Variables: {n_vars}, Restricciones: {n_cons}")
    print(f"Objetivo: {sentido} - Coeficientes: {c}")
    print(f"Matriz A: {A}")
    print(f"Vector b: {b}")
    print(f"Signos: {signs}")
    
    # Crear variables
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
    
    print(f"\nVariables slack: {slack}")
    print(f"Variables exceso: {exceso}")
    print(f"Variables artificiales: {artificial}")
    print(f"Base inicial: {base}")
    
    headers = var_names + slack + exceso + artificial
    print(f"Headers: {headers}")
    
    # Construir tabla inicial
    print("\n=== CONSTRUCCIÓN TABLA INICIAL ===")
    
    # Fila objetivo Fase I (minimizar suma de artificiales)
    fila_obj = [Fraction(0)] * (len(var_names) + len(slack) + len(exceso))
    fila_obj += [Fraction(1)] * len(artificial)
    fila_obj.append(Fraction(0))
    
    print(f"Fila objetivo Fase I (antes de ajustar): {fila_obj}")
    
    tbl = [fila_obj]
    
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
        print(f"Fila restricción {i+1}: {row}")
    
    # Ajustar fila objetivo Fase I
    print(f"\n=== AJUSTE FILA OBJETIVO FASE I ===")
    print(f"Fila objetivo antes del ajuste: {tbl[0]}")
    
    for i, var in enumerate(base):
        if var.startswith("a"):
            idx = headers.index(var)
            print(f"Ajustando por variable artificial {var} (columna {idx})")
            print(f"  Restando fila {i+1}: {tbl[i+1]}")
            for j in range(len(tbl[0])):
                tbl[0][j] -= tbl[i+1][j]
            print(f"  Fila objetivo después: {tbl[0]}")
    
    print(f"\nTabla inicial completa:")
    print(f"Headers: {['Base'] + headers + ['b']}")
    print(f"Fila obj: {['W'] + [str(x) for x in tbl[0]]}")
    for i in range(len(base)):
        print(f"Fila {base[i]}: {[base[i]] + [str(x) for x in tbl[i+1]]}")
    
    return tbl, headers, base

if __name__ == "__main__":
    # Problema de la imagen
    payload = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2000, 500],
        "A": [[2, 3], [3, 6]], 
        "b": [36, 60],
        "signs": [">=", ">="],
        "obj_type": "min"
    }
    
    debug_dos_fases(payload)
