from fractions import Fraction
from typing import List, Dict, Any
import copy
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import uvicorn

class SimplexDosFasesTablaCompleta:
    """
    Implementación del método de dos fases para problemas de programación lineal.
    Permite ver cada iteración y el estado de la tabla en cada paso.
    """

    def __init__(self):
        pass

    def solve_from_data(
        self,
        n_vars: int,
        n_cons: int,
        c: List[float],
        A: List[List[float]],
        b: List[float],
        signs: List[str],
        obj_type: str
    ) -> Dict[str, Any]:
        """
        Resuelve un problema de PL usando el método de dos fases a partir de datos directos.
        Guarda cada iteración de la tabla simplex para su posterior análisis.
        """
        # Inicialización de parámetros
        self.n_vars = n_vars
        self.n_cons = n_cons
        self.c = [Fraction(str(x)) for x in c]
        self.A = [[Fraction(str(x)) for x in row] for row in A]
        self.b = [Fraction(str(x)) for x in b]
        self.signs = signs
        self.obj_type = obj_type.lower()

        # Variables para seguimiento de iteraciones
        self.iteraciones_fase1 = []
        self.iteraciones_fase2 = []

        # --- Paso 1: Resolver con el método de dos fases ---
        resultado = self.solve_dos_fases()

        return resultado

    def solve_dos_fases(self) -> Dict[str, Any]:
        """
        Método principal para resolver el problema usando el método de dos fases.
        """
        # --- FASE I: Preparación y resolución ---
        self.preparar_fase1()
        self.ejecutar_simplex_fase1()

        # Comprobación de factibilidad
        obj_fase1 = self.tbl_fase1[0][-1]
        if abs(obj_fase1) > 1e-8:
            return {
                "error": "El problema es INFACTIBLE (la suma de artificiales no es cero en Fase I)",
                "fase1": {"factible": False, "iteraciones": self.iteraciones_fase1},
                "fase2": {"iteraciones": []}
            }

        # --- FASE II: Eliminación de artificiales y optimización de la función objetivo original ---
        self.preparar_fase2()
        self.ejecutar_simplex_fase2()

        # --- SOLUCIÓN FINAL ---
        sol = {var: 0 for var in self.headers2}
        for i, var in enumerate(self.base2):
            if var and var in sol:
                sol[var] = float(self.tbl2[i+1][-1])
        z_final = float(self.tbl2[0][-1])
        return {
            "fase1": {"factible": True, "iteraciones": self.iteraciones_fase1},
            "fase2": {
                "optimo": True,
                "valor_objetivo": z_final,
                "solucion": sol,
                "iteraciones": self.iteraciones_fase2
            }
        }

    def preparar_fase1(self):
        """
        Prepara los datos y la tabla para iniciar la Fase I del método de dos fases.
        """
        # Inicialización de variables adicionales y base
        self.var_names = [f"x{i+1}" for i in range(self.n_vars)]
        self.slack, self.exceso, self.artificial = [], [], []
        self.base = []
        for i, sign in enumerate(self.signs):
            if sign == "<=":
                s = f"s{i+1}"
                self.slack.append(s)
                self.base.append(s)
            elif sign == ">=":
                e = f"e{i+1}"
                a = f"a{i+1}"
                self.exceso.append(e)
                self.artificial.append(a)
                self.base.append(a)
            elif sign == "=":
                a = f"a{i+1}"
                self.artificial.append(a)
                self.base.append(a)
        self.var_names += self.slack + self.exceso + self.artificial

        # --- Construcción de la tabla inicial para Fase I ---
        tbl = []
        # Fila objetivo Fase I (minimizar suma de artificiales)
        fila_obj = [Fraction(0)] * (len(self.var_names) - len(self.artificial))
        fila_obj += [Fraction(1)] * len(self.artificial)
        fila_obj.append(Fraction(0))
        tbl.append(fila_obj)
        # Filas de restricciones
        for i in range(self.n_cons):
            row = list(self.A[i])
            row += [Fraction(0)] * (len(self.var_names) - self.n_vars)
            if self.signs[i] == "<=":
                idx = self.var_names.index(f"s{i+1}")
                row[idx] = Fraction(1)
            elif self.signs[i] == ">=":
                idx_e = self.var_names.index(f"e{i+1}")
                idx_a = self.var_names.index(f"a{i+1}")
                row[idx_e] = Fraction(-1)
                row[idx_a] = Fraction(1)
            elif self.signs[i] == "=":
                idx_a = self.var_names.index(f"a{i+1}")
                row[idx_a] = Fraction(1)
            row.append(self.b[i])
            tbl.append(row)
        # Ajustar la fila objetivo de Fase I restando las filas de artificiales en la base
        for i, var in enumerate(self.base):
            if var and var.startswith("a"):
                idx = self.var_names.index(var)
                for j in range(len(tbl[0])):
                    tbl[0][j] -= tbl[i+1][j]
        self.tbl_fase1 = tbl
        self.headers_fase1 = ["Base"] + self.var_names + ["b"]
        self._save_iteracion_fase1(self.tbl_fase1, self.base, optima=False)

    def ejecutar_simplex_fase1(self):
        """
        Ejecuta el algoritmo simplex para la Fase I, buscando una solución factible.
        """
        tbl = copy.deepcopy(self.tbl_fase1)
        base = self.base[:]
        paso = 1
        max_iteraciones = 100  # Límite de seguridad para evitar bucles infinitos

        while paso <= max_iteraciones:
            # Buscar columna pivote
            pivot_col = -1
            max_value = Fraction(0)
            for j, val in enumerate(tbl[0][:-1]):
                if val > max_value:  # Buscamos el más positivo
                    max_value = val
                    pivot_col = j
            if pivot_col == -1:
                break  # Ya es óptimo

            # Buscar fila pivote usando test de razón
            min_ratio = None
            pivot_row = None
            for i in range(1, len(tbl)):
                col = tbl[i][pivot_col]
                if col > 0:  # Solo considerar positivos
                    ratio = tbl[i][-1] / col
                    if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                        min_ratio = ratio
                        pivot_row = i
            if pivot_row is None:
                self._save_iteracion_fase1(tbl, base, optima=False, ilimitado=True)
                break  # ilimitado

            # Pivoteo
            div = tbl[pivot_row][pivot_col]
            tbl[pivot_row] = [x / div for x in tbl[pivot_row]]
            for i in range(len(tbl)):
                if i != pivot_row:
                    coef = tbl[i][pivot_col]
                    tbl[i] = [x - coef * y for x, y in zip(tbl[i], tbl[pivot_row])]
            base[pivot_row-1] = self.var_names[pivot_col]
            paso += 1
            self._save_iteracion_fase1(tbl, base, optima=False)
        self.tbl_fase1 = tbl
        self.base_fase1 = base
        self._save_iteracion_fase1(tbl, base, optima=True)

    def preparar_fase2(self):
        """
        Prepara los datos y la tabla para iniciar la Fase II del método de dos fases.
        """
        cols_keep = [i for i, v in enumerate(self.var_names) if not v.startswith("a")]
        self.headers2 = [self.var_names[i] for i in cols_keep]
        tbl2 = []
        for row in self.tbl_fase1:
            tbl2.append([row[i] for i in cols_keep] + [row[-1]])
        # Nueva base para Fase II
        base2 = []
        for i, bvar in enumerate(self.base_fase1):
            if bvar and bvar.startswith("a"):
                found = False
                for j, h in enumerate(self.headers2):
                    if abs(float(tbl2[i+1][j]) - 1) < 1e-8:
                        # Verificar si es la única no-cero en su columna
                        is_basic = True
                        for k in range(1, len(tbl2)):
                            if k != i+1 and abs(float(tbl2[k][j])) > 1e-8:
                                is_basic = False
                                break
                        if is_basic:
                            base2.append(h)
                            found = True
                            break
                if not found:
                    base2.append(None)
            else:
                base2.append(bvar)
        # Fila objetivo (función original)
        fila_obj2 = []
        for h in self.headers2:
            if h.startswith("x"):
                idx = int(h[1:]) - 1
                coef = self.c[idx]
                fila_obj2.append(-coef if self.obj_type == "max" else coef)
            else:
                fila_obj2.append(Fraction(0))
        fila_obj2.append(Fraction(0))
        # Ajuste fila 0 eliminando variables básicas presentes en R0
        for i, bvar in enumerate(base2):
            if bvar and bvar in self.headers2:
                idx = self.headers2.index(bvar)
                coef_R0 = fila_obj2[idx]
                if coef_R0 != 0:
                    for j in range(len(fila_obj2)):
                        fila_obj2[j] -= coef_R0 * tbl2[i+1][j]
        tbl2[0] = fila_obj2
        self.tbl2 = tbl2
        self.headers_fase2 = ["Base"] + self.headers2 + ["b"]
        self.base2 = base2
        self._save_iteracion_fase2(self.tbl2, self.base2, optima=False)

    def ejecutar_simplex_fase2(self):
        """
        Ejecuta el algoritmo simplex para la Fase II, buscando la solución óptima.
        """
        tbl = copy.deepcopy(self.tbl2)
        base = self.base2[:]
        paso = 1
        max_iter = 100
        sentido = self.obj_type
        while paso <= max_iter:
            # Buscar columna pivote
            if sentido == "max":
                min_value = Fraction(0)
                pivot_col = -1
                for j, val in enumerate(tbl[0][:-1]):
                    if val < min_value:
                        min_value = val
                        pivot_col = j
            else:
                max_value = Fraction(0)
                pivot_col = -1
                for j, val in enumerate(tbl[0][:-1]):
                    if val > max_value:
                        max_value = val
                        pivot_col = j
            if pivot_col == -1:
                break  # óptimo

            # Buscar fila pivote
            min_ratio = None
            pivot_row = None
            for i in range(1, len(tbl)):
                col = tbl[i][pivot_col]
                if col > 0:
                    ratio = tbl[i][-1] / col
                    if ratio >= 0 and (min_ratio is None or ratio < min_ratio):
                        min_ratio = ratio
                        pivot_row = i
            if pivot_row is None:
                self._save_iteracion_fase2(tbl, base, optima=False, ilimitado=True)
                break  # ilimitado

            # Pivoteo
            div = tbl[pivot_row][pivot_col]
            tbl[pivot_row] = [x / div for x in tbl[pivot_row]]
            for i in range(len(tbl)):
                if i != pivot_row:
                    coef = tbl[i][pivot_col]
                    tbl[i] = [x - coef * y for x, y in zip(tbl[i], tbl[pivot_row])]
            base[pivot_row-1] = self.headers2[pivot_col]
            paso += 1
            self._save_iteracion_fase2(tbl, base, optima=False)
        self.tbl2 = tbl
        self.base2 = base
        self._save_iteracion_fase2(tbl, base, optima=True)

    def _save_iteracion_fase1(self, tbl, base, optima=False, ilimitado=False):
        rows = []
        rows.append(["W"] + [str(x) for x in tbl[0]])
        for i, b in enumerate(base):
            rows.append([b if b is not None else "-"] + [str(x) for x in tbl[i+1]])
        self.iteraciones_fase1.append({
            "headers": self.headers_fase1,
            "rows": rows,
            "optima": optima,
            "ilimitado": ilimitado,
        })

    def _save_iteracion_fase2(self, tbl, base, optima=False, ilimitado=False):
        rows = []
        rows.append(["Z"] + [str(x) for x in tbl[0]])
        for i, b in enumerate(base):
            rows.append([b if b is not None else "-"] + [str(x) for x in tbl[i+1]])
        self.iteraciones_fase2.append({
            "headers": self.headers_fase2,
            "rows": rows,
            "optima": optima,
            "ilimitado": ilimitado,
        })


# --- API FastAPI ---
app = FastAPI(title="Dos Fases API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolverRequest(BaseModel):
    n_vars: int
    n_cons: int
    c: List[float]
    A: List[List[float]]
    b: List[float]
    signs: List[str]
    obj_type: Literal["max", "min"]
    method: Literal["dosfases"] = "dosfases"

@app.post("/solve")
async def solve_problem(data: SolverRequest):
    print("Payload recibido:", data.dict())  # <-- Debug: muestra el payload recibido
    try:
        solver = SimplexDosFasesTablaCompleta()
        result = solver.solve_from_data(
            n_vars=data.n_vars,
            n_cons=data.n_cons,
            c=data.c,
            A=data.A,
            b=data.b,
            signs=data.signs,
            obj_type=data.obj_type
        )
        return result
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("dosfases_backend:app", host="0.0.0.0", port=8003, reload=False)