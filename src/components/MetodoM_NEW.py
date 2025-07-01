from fractions import Fraction
from typing import List, Dict, Any
import copy

class SimplexTablaInicialCompleta:
    """
    Implementación del método de la Gran M para problemas de programación lineal.
    Esta clase permite ingresar un problema, construir la tabla inicial con penalizaciones
    para variables artificiales y ejecutar el proceso simplex, mostrando cada paso.
    """

    def __init__(self):
        # Número de variables originales (x1, x2, ...)
        self.n_vars = 0
        # Número de restricciones
        self.n_cons = 0
        # Tipo de problema: 'max' o 'min'
        self.original_obj_type = ""
        # Coeficientes de la función objetivo original
        self.c = []
        # Matriz de coeficientes de restricciones
        self.A = []
        # Lados derechos (vector b)
        self.b = []
        # Signos de las restricciones (<=, >=, =)
        self.signs = []
        # Lista de nombres de todas las variables (originales + adicionales)
        self.var_names = []
        # Variables actualmente en la base
        self.base_vars = []
        # Símbolo para la penalización (M)
        self.M = "M"
        # Fila de la función objetivo penalizada (con -M en artificiales)
        self.penal_obj_row = []
        # Fila 0 para el tableau simplex (puede ser distinta según el tipo)
        self.simplex_obj_row = []
        # Toda la tabla simplex (fila 0 + restricciones)
        self.tableau = []
        # Indica si se convirtió un problema de minimización a maximización
        self.converted_to_max = False

    def build_all(self):
        """
        Construye la tabla inicial simplex con variables de holgura, exceso y artificiales,
        arma la función objetivo penalizada y la fila 0 del tableau.
        """
        # Si es minimización, se convierte a maximización multiplicando por -1
        if self.original_obj_type == "min":
            self.c = [-coef for coef in self.c]
            self.converted_to_max = True
        else:
            self.converted_to_max = False

        # Nombres de las variables originales
        self.var_names = [f"x{i+1}" for i in range(self.n_vars)]
        slack_vars, exceso_vars, artificial_vars = [], [], []
        base_vars = []
        # Según el tipo de restricción, agrega variables de holgura, exceso y artificiales
        for i, sign in enumerate(self.signs):
            if sign == "<=":
                slack_vars.append(f"s{i+1}")
                base_vars.append(f"s{i+1}")
            elif sign == ">=":
                exceso_vars.append(f"e{i+1}")
                artificial_vars.append(f"a{i+1}")
                base_vars.append(f"a{i+1}")
            elif sign == "=":
                artificial_vars.append(f"a{i+1}")
                base_vars.append(f"a{i+1}")
        # Actualiza la lista de variables
        self.var_names += slack_vars + exceso_vars + artificial_vars
        self.base_vars = base_vars

        # Construye la función objetivo penalizada (con -M en artificiales)
        penal_obj_row = []
        penal_obj_row += self.c
        penal_obj_row += [0] * len(slack_vars)
        penal_obj_row += [0] * len(exceso_vars)
        for _ in artificial_vars:
             penal_obj_row.append("-M")
        self.penal_obj_row = penal_obj_row

        # Construye la fila 0 para el tableau simplex (cambia signo si es max o min)
        if self.original_obj_type == "min":
            self.simplex_obj_row = self.penal_obj_row.copy()
        else:
            self.simplex_obj_row = []
            for coef in self.penal_obj_row:
                if isinstance(coef, (int, float)):
                    self.simplex_obj_row.append(-coef)
                elif coef == "-M":
                    self.simplex_obj_row.append("+M")
                elif coef == "M":
                    self.simplex_obj_row.append("-M")
                elif coef == 0 or coef == "0":
                    self.simplex_obj_row.append(0)
                else:
                    self.simplex_obj_row.append(coef)

        # Construye las filas del tableau simplex para las restricciones
        tableau_rows = []
        for i, row in enumerate(self.A):
            tableau_row = list(row)
            tableau_row += [0] * (len(self.var_names) - self.n_vars)
            if self.signs[i] == "<=":
                idx = self.var_names.index(f"s{i+1}")
                tableau_row[idx] = 1
            elif self.signs[i] == ">=":
                idx_e = self.var_names.index(f"e{i+1}")
                idx_a = self.var_names.index(f"a{i+1}")
                tableau_row[idx_e] = -1
                tableau_row[idx_a] = 1
            elif self.signs[i] == "=":
                idx_a = self.var_names.index(f"a{i+1}")
                tableau_row[idx_a] = 1
            tableau_row.append(self.b[i])
            tableau_rows.append(tableau_row)
        # Junta la fila 0 y las filas de restricciones en el tableau
        self.tableau = [self.simplex_obj_row + [0]] + tableau_rows

    def to_algebraic_tableau(self):
        """
        Convierte la tabla simplex a una versión algebraica donde cada celda
        es una tupla (parte real, parte con M) para poder operar con coeficientes simbólicos.
        """
        artificial_indices = [i for i, base in enumerate(self.base_vars) if base.startswith("a")]
        r0_original = []
        if self.original_obj_type == "min":
            for coef in self.penal_obj_row:
                if coef == "-M":
                    r0_original.append("+M")
                elif coef == "M":
                    r0_original.append("-M")
                elif isinstance(coef, (int, float)):
                    r0_original.append(abs(coef) if coef < 0 else -abs(coef))
                else:
                    r0_original.append(coef)
        else:
            r0_original = self.tableau[0][:-1]
        tabla_alg = []
        # Convierte R0
        fila_alg = []
        for j in range(len(r0_original)):
            r0_orig_val = r0_original[j]
            suma_artificiales = 0
            for idx in artificial_indices:
                coef = self.tableau[idx+1][j]
                suma_artificiales += coef
            if isinstance(r0_orig_val, (int, float)):
                real_part = Fraction(r0_orig_val)
                m_part = -Fraction(suma_artificiales)
            else:
                r0_str = str(r0_orig_val)
                if r0_str == "+M" or r0_str == "M":
                    real_part = Fraction(0)
                    m_part = 1 - Fraction(suma_artificiales)
                elif r0_str == "-M":
                    real_part = Fraction(0)
                    m_part = -1 - Fraction(suma_artificiales)
                else:
                    try:
                        real_part = Fraction(float(r0_str))
                        m_part = -Fraction(suma_artificiales)
                    except:
                        real_part = Fraction(0)
                        m_part = -Fraction(suma_artificiales)
            fila_alg.append((real_part, m_part))
        # RHS
        rhs_orig = self.tableau[0][-1]
        suma_rhs_artificiales = sum(self.tableau[idx+1][-1] for idx in artificial_indices)
        if isinstance(rhs_orig, (int, float)):
            rhs_real = Fraction(rhs_orig)
            rhs_m = -Fraction(suma_rhs_artificiales)
        else:
            rhs_real = Fraction(0)
            rhs_m = -Fraction(suma_rhs_artificiales)
        fila_alg.append((rhs_real, rhs_m))
        tabla_alg.append(fila_alg)
        # Restricciones
        for row in self.tableau[1:]:
            fila = []
            for val in row:
                fila.append((Fraction(val), Fraction(0)))
            tabla_alg.append(fila)
        return tabla_alg

    def solve_from_data(self, n_vars: int, n_cons: int, c: List[float], A: List[List[float]], b: List[float], signs: List[str], obj_type: str) -> Dict[str, Any]:
        """
        Resuelve el problema usando los datos dados y devuelve todos los pasos y tablas como JSON serializable.
        """
        # Inicializa los datos
        self.n_vars = n_vars
        self.n_cons = n_cons
        self.c = c
        self.A = A
        self.b = b
        self.signs = signs
        self.original_obj_type = obj_type
        self.build_all()

        # Paso 1: función objetivo penalizada
        penalized_obj = self._get_penalized_obj_function()
        # Paso 2: fila 0 simplex
        simplex_obj = self._get_simplex_obj_row()
        # Paso 3: tabla inicial
        initial_tableau = self._get_initial_tableau()
        # Paso 4: solución básica inicial
        sbfi = self._get_sbfi()
        # Paso 5: renglón 0 nuevo
        r0_nuevo = self._get_renglon_0_nuevo()
        # Paso 6: iteraciones simplex
        iteraciones = self._get_simplex_iteraciones()

        return {
            "penalized_obj": penalized_obj,
            "simplex_obj": simplex_obj,
            "initial_tableau": initial_tableau,
            "sbfi": sbfi,
            "r0_nuevo": r0_nuevo,
            "iteraciones": iteraciones
        }

    def _get_penalized_obj_function(self):
        partes = []
        for coef, var in zip(self.penal_obj_row, self.var_names):
            if coef == 0 or coef == "0":
                continue
            if coef == "-M":
                partes.append(f"- M{var}")
            elif coef == "M":
                partes.append(f"+ M{var}")
            elif isinstance(coef, (int, float)):
                partes.append(f"{'+' if coef > 0 else '-'} {abs(coef)}{var}")
            else:
                partes.append(f"{coef}{var}")
        funcion = " ".join(partes).lstrip("+ ").replace("+ -", "- ")
        return {"expr": f"Max Z' = {funcion}", "terms": partes}

    def _get_simplex_obj_row(self):
        partes = []
        if self.original_obj_type == "min":
            for coef, var in zip(self.penal_obj_row, self.var_names):
                if coef == 0 or coef == "0":
                    continue
                if coef == "-M":
                    partes.append(f"+ M{var}")
                elif coef == "M":
                    partes.append(f"- M{var}")
                elif isinstance(coef, (int, float)):
                    partes.append(f"{'+' if coef < 0 else '-'} {abs(coef)}{var}")
                else:
                    partes.append(f"{coef}{var}")
            expresion = " ".join(partes).lstrip("+ ").replace("+ -", "- ")
            return {"expr": f"-Z' {expresion} = 0", "terms": partes}
        else:
            for coef, var in zip(self.simplex_obj_row, self.var_names):
                if coef == 0 or coef == "0":
                    continue
                if coef == "+M":
                    partes.append(f"+ M{var}")
                elif coef == "M":
                    partes.append(f"+ M{var}")
                elif coef == "-M":
                    partes.append(f"- M{var}")
                elif isinstance(coef, (int, float)):
                    partes.append(f"{'+' if coef > 0 else '-'} {abs(coef)}{var}")
                else:
                    partes.append(f"{coef}{var}")
            expresion = " ".join(partes).lstrip("+ ").replace("+ -", "- ")
            return {"expr": f"Z' {expresion} = 0", "terms": partes}

    def _get_initial_tableau(self):
        headers = ["Base"] + self.var_names + ["b"]
        rows = []
        zname = "-Z'" if self.original_obj_type == "min" else "  Z'"
        row0 = []
        if self.original_obj_type == "min":
            for coef in self.penal_obj_row:
                if coef == "-M":
                    row0.append("+M")
                elif coef == "M":
                    row0.append("-M")
                elif isinstance(coef, (int, float)):
                    row0.append(f"{abs(coef)}" if coef < 0 else f"-{abs(coef)}")
                else:
                    row0.append(coef)
        else:
            for coef in self.simplex_obj_row:
                row0.append(coef)
        rows.append({"base": zname, "values": row0 + [self.tableau[0][-1]]})
        for base, row in zip(self.base_vars, self.tableau[1:]):
            rows.append({"base": base, "values": row})
        return {"headers": headers, "rows": rows}

    def _get_sbfi(self):
        variable_values = {var: 0 for var in self.var_names}
        for base, row in zip(self.base_vars, self.tableau[1:]):
            variable_values[base] = row[-1]
        artificial_sum = sum(variable_values[var] for var in self.var_names if var.startswith("a"))
        z_val = f"{self.M}*({artificial_sum}) = {artificial_sum}{self.M}" if any(var.startswith("a") for var in self.var_names) else "0"
        return {"variables": variable_values, "z": z_val}

    def _get_renglon_0_nuevo(self):
        artificial_indices = [i for i, base in enumerate(self.base_vars) if base.startswith("a")]
        r0_original = []
        if self.original_obj_type == "min":
            for coef in self.penal_obj_row:
                if coef == "-M":
                    r0_original.append("+M")
                elif coef == "M":
                    r0_original.append("-M")
                elif isinstance(coef, (int, float)):
                    r0_original.append(abs(coef) if coef < 0 else -abs(coef))
                else:
                    r0_original.append(coef)
        else:
            r0_original = self.tableau[0][:-1]
        r0_nuevo = []
        for j in range(len(r0_original)):
            r0_orig_val = r0_original[j]
            suma_artificiales = 0
            for idx in artificial_indices:
                coef = self.tableau[idx+1][j]
                suma_artificiales += coef
            if isinstance(r0_orig_val, (int, float)):
                real_part = r0_orig_val
                m_part = -suma_artificiales
            else:
                r0_str = str(r0_orig_val)
                if r0_str == "+M" or r0_str == "M":
                    real_part = 0
                    m_part = 1 - suma_artificiales
                elif r0_str == "-M":
                    real_part = 0
                    m_part = -1 - suma_artificiales
                else:
                    try:
                        real_part = float(r0_str)
                        m_part = -suma_artificiales
                    except:
                        real_part = 0
                        m_part = -suma_artificiales
            # Notación simbólica
            if abs(real_part) < 1e-8 and abs(m_part) < 1e-8:
                resultado = "0"
            elif abs(real_part) < 1e-8:
                if m_part == 1:
                    resultado = "M"
                elif m_part == -1:
                    resultado = "-M"
                else:
                    resultado = f"{m_part:g}M"
            elif abs(m_part) < 1e-8:
                resultado = f"{real_part:g}"
            else:
                if m_part > 0:
                    if m_part == 1:
                        resultado = f"{real_part:g}+M"
                    else:
                        resultado = f"{real_part:g}+{m_part:g}M"
                else:
                    if m_part == -1:
                        resultado = f"{real_part:g}-M"
                    else:
                        resultado = f"{real_part:g}{m_part:g}M"
            r0_nuevo.append(resultado)
        # RHS
        rhs_orig = self.tableau[0][-1]
        suma_rhs_artificiales = sum(self.tableau[idx+1][-1] for idx in artificial_indices)
        if isinstance(rhs_orig, (int, float)):
            rhs_real = rhs_orig
            rhs_m = -suma_rhs_artificiales
        else:
            rhs_real = 0
            rhs_m = -suma_rhs_artificiales
        if abs(rhs_real) < 1e-8 and abs(rhs_m) < 1e-8:
            rhs_resultado = "0"
        elif abs(rhs_real) < 1e-8:
            if rhs_m == 1:
                rhs_resultado = "M"
            elif rhs_m == -1:
                rhs_resultado = "-M"
            else:
                rhs_resultado = f"{rhs_m:g}M"
        elif abs(rhs_m) < 1e-8:
            rhs_resultado = f"{rhs_real:g}"
        else:
            if rhs_m > 0:
                if rhs_m == 1:
                    rhs_resultado = f"{rhs_real:g}+M"
                else:
                    rhs_resultado = f"{rhs_real:g}+{rhs_m:g}M"
            else:
                if rhs_m == -1:
                    rhs_resultado = f"{rhs_real:g}-M"
                else:
                    rhs_resultado = f"{rhs_real:g}{rhs_m:g}M"
        r0_nuevo.append(rhs_resultado)
        # Tabla resultante
        headers = ["Base"] + self.var_names + ["b"]
        rows = []
        rows.append({"base": "R0*", "values": r0_nuevo})
        for base, row in zip(self.base_vars, self.tableau[1:]):
            rows.append({"base": base, "values": row})
        return {"headers": headers, "rows": rows}

    def _get_simplex_iteraciones(self):
        # Devuelve una lista de iteraciones, cada una con la tabla y la base
        tabla_alg = self.to_algebraic_tableau()
        base_vars = self.base_vars.copy()
        iteraciones = []
        paso = 1
        while True:
            iteracion = {
                "paso": paso,
                "tabla": self._serialize_tableau_alg(tabla_alg, base_vars),
                "base": copy.deepcopy(base_vars)
            }
            iteraciones.append(iteracion)
            
            r0 = tabla_alg[0]            # 1. Buscar columna pivote: más negativa en M, luego real
            j_pivot = None
            
            for j in range(len(r0)-1):
                real, m = r0[j]
                # Si hay coeficiente M negativo, es prioritario
                if m < 0:
                    if j_pivot is None:
                        j_pivot = j
                    else:
                        prev_real, prev_m = r0[j_pivot]
                        if m < prev_m or (m == prev_m and real < prev_real):
                            j_pivot = j
                # Si no hay M negativo, buscar parte real negativa
                elif m == 0 and real < 0:
                    if j_pivot is None:
                        j_pivot = j
                    else:
                        prev_real, prev_m = r0[j_pivot]
                        if prev_m > 0 or (prev_m == 0 and real < prev_real):
                            j_pivot = j
            
            if j_pivot is None:
                iteracion["optima"] = True
                break
            # 2. Buscar fila pivote
            min_ratio = None
            i_pivot = None
            for i in range(1, len(tabla_alg)):
                real, m = tabla_alg[i][j_pivot]
                rhs_real, rhs_m = tabla_alg[i][-1]
                if m == 0 and real > 0:
                    ratio = rhs_real / real
                    if (min_ratio is None) or (ratio < min_ratio):
                        min_ratio = ratio
                        i_pivot = i
            if i_pivot is None:
                iteracion["ilimitado"] = True
                break
            # 3. Normalizar fila pivote
            pivote_real, pivote_m = tabla_alg[i_pivot][j_pivot]
            if pivote_m != 0 or pivote_real == 0:
                iteracion["pivote_invalido"] = True
                break
            nueva_fila_pivote = []
            for cell in tabla_alg[i_pivot]:
                real, m = cell
                nueva_fila_pivote.append((real/pivote_real, m/pivote_real))
            # 4. Actualizar todas las filas
            nueva_tabla = []
            for i, row in enumerate(tabla_alg):
                if i == i_pivot:
                    nueva_tabla.append(nueva_fila_pivote)
                    continue
                factor_real, factor_m = row[j_pivot]
                nueva_fila = []
                for cell, rp in zip(row, nueva_fila_pivote):
                    ci, ciM = cell
                    rp_real, rp_m = rp
                    new_real = ci - factor_real * rp_real
                    new_m = ciM - factor_real * rp_m - factor_m * rp_real
                    nueva_fila.append((new_real, new_m))
                nueva_tabla.append(nueva_fila)            # Cambiar base
            base_vars[i_pivot-1] = self.var_names[j_pivot]
            tabla_alg = nueva_tabla
            paso += 1
            
        # Marcar la última iteración como óptima
        if iteraciones:
            iteraciones[-1]["optima"] = True
            
        return iteraciones

    def _serialize_tableau_alg(self, tabla_alg, base_vars):
        headers = ["Base"] + self.var_names + ["b"]
        rows = []
        for i, row in enumerate(tabla_alg):
            if i == 0:
                name = "R0*"
            else:
                name = base_vars[i-1]
            values = []
            for cell in row:
                real, m = cell
                # Presenta cada celda en formato adecuado
                if abs(real) < 1e-8 and abs(m) < 1e-8:
                    values.append("0")
                elif abs(real) < 1e-8:
                    if m == 1:
                        values.append("M")
                    elif m == -1:
                        values.append("-M")
                    else:
                        values.append(f"{m}M")
                elif abs(m) < 1e-8:
                    values.append(f"{real}")
                else:
                    if m > 0:
                        if m == 1:
                            values.append(f"{real}+M")
                        else:
                            values.append(f"{real}+{m}M")
                    else:
                        if m == -1:
                            values.append(f"{real}-M")
                        else:
                            values.append(f"{real}{m}M")
            rows.append({"base": name, "values": values})
        return {"headers": headers, "rows": rows}