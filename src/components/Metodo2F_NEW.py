#!/usr/bin/env python3
"""
Módulo Simplex Completo - Método de Dos Fases con Fracciones Exactas
Integrado con API para frontend React
"""

from fractions import Fraction
from typing import List, Dict, Any, Tuple, Optional, Union

class SimplexCompleto:
    def __init__(self):
        self.variables = []
        self.artificiales = []
        self.n_vars_decision = 0
        self.objetivo_tipo = "min"
        
    def fraction_to_string(self, frac: Fraction) -> str:
        """Convierte una fracción a string, manteniendo enteros como enteros"""
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"{frac.numerator}/{frac.denominator}"
    
    def preparar_ecuaciones(self, n_vars: int, n_cons: int, A: List[List[float]], 
                          b: List[float], signos: List[str]) -> Tuple[List[str], List[str], List[List[Fraction]]]:
        """Prepara el sistema de ecuaciones con variables de holgura y artificiales"""
        S_names = []
        artificiales = []
        filas_coef = []

        S_count = 0
        A_count = 0
        
        # Contar variables auxiliares necesarias
        for i in range(n_cons):
            if signos[i] in ("<=", ">="):
                S_count += 1
                S_names.append(f"S{S_count}")
            if signos[i] in (">=", "="):
                A_count += 1
                artificiales.append(f"A{A_count}")

        # Lista completa de variables
        variables = [f"x{i+1}" for i in range(n_vars)] + S_names + artificiales
        n_S = len(S_names)
        n_A = len(artificiales)

        # Construir matriz de restricciones
        S_idx = 0
        A_idx = 0
        for i in range(n_cons):
            fila = [Fraction(0)] * (n_vars + n_S + n_A)
            
            # Coeficientes de variables de decisión
            for j in range(n_vars):
                fila[j] = Fraction(A[i][j]).limit_denominator()
            
            # Agregar variables auxiliares según el signo
            if signos[i] == "<=":
                fila[n_vars + S_idx] = Fraction(1)  # +S
                S_idx += 1
            elif signos[i] == ">=":
                fila[n_vars + S_idx] = Fraction(-1)  # -S
                fila[n_vars + n_S + A_idx] = Fraction(1)  # +A
                S_idx += 1
                A_idx += 1
            elif signos[i] == "=":
                fila[n_vars + n_S + A_idx] = Fraction(1)  # +A
                A_idx += 1
                
            filas_coef.append(fila)
            
        return variables, artificiales, filas_coef

    def fila_objetivo_fase1(self, variables: List[str], artificiales: List[str]) -> List[Fraction]:
        """Crea la fila objetivo para Fase 1 (minimizar variables artificiales)"""
        return [Fraction(-1) if v in artificiales else Fraction(0) for v in variables]

    def tabla_fase1_actualizada(self, variables: List[str], artificiales: List[str], 
                               filas_coef: List[List[Fraction]], b: List[float]) -> List[List[Fraction]]:
        """Construye la tabla inicial de Fase 1 con R0 actualizada"""
        fila_z = self.fila_objetivo_fase1(variables, artificiales)
        b_z = Fraction(0)
        
        # Actualizar R0 sumando filas de variables artificiales
        for vA in artificiales:
            col = variables.index(vA)
            for i, fila in enumerate(filas_coef):
                if fila[col] == 1:
                    fila_z = [fz + fj for fz, fj in zip(fila_z, fila)]
                    b_z += Fraction(b[i]).limit_denominator()
                    break
        
        # Construir tabla completa
        tabla = [fila_z + [b_z]]
        for i, fila in enumerate(filas_coef):
            tabla.append(list(fila) + [Fraction(b[i]).limit_denominator()])
            
        return tabla

    def identificar_pivote_fase1(self, tabla: List[List[Fraction]], 
                                n_vars: int) -> Tuple[Optional[int], Optional[int]]:
        """Identifica columna y fila pivote para Fase 1"""
        z = tabla[0]
        
        # Buscar el coeficiente más positivo en las primeras n_vars columnas
        max_pos = max(z[:n_vars])
        if max_pos <= 0:
            return None, None  # Óptimo alcanzado
            
        col_pivote = z.index(max_pos)
        
        # Calcular ratios para encontrar fila pivote
        ratios = []
        for i, fila in enumerate(tabla[1:], 1):
            coef = fila[col_pivote]
            if coef > 0:
                ratio = fila[-1] / coef
                ratios.append((ratio, i))
        
        if not ratios:
            return col_pivote, None  # Solución ilimitada
            
        _, fila_pivote = min(ratios)
        return col_pivote, fila_pivote

    def identificar_pivote_fase2(self, tabla: List[List[Fraction]], 
                                objetivo: str) -> Tuple[Optional[int], Optional[int]]:
        """Identifica columna y fila pivote para Fase 2"""
        z = tabla[0]
        
        if objetivo == "max":
            # Maximización: buscar el más negativo
            min_val = min(z[:-1])  # Excluir columna b
            if min_val >= 0:
                return None, None  # Óptimo alcanzado
            col_pivote = z.index(min_val)
        else:  # minimización
            # Minimización: buscar el más positivo
            max_val = max(z[:-1])  # Excluir columna b
            if max_val <= 0:
                return None, None  # Óptimo alcanzado
            col_pivote = z.index(max_val)
        
        # Calcular ratios para encontrar fila pivote
        ratios = []
        for i, fila in enumerate(tabla[1:], 1):
            coef = fila[col_pivote]
            if coef > 0:
                ratio = fila[-1] / coef
                ratios.append((ratio, i))
        
        if not ratios:
            return col_pivote, None  # Solución ilimitada
            
        _, fila_pivote = min(ratios)
        return col_pivote, fila_pivote

    def realizar_pivoteo(self, tabla: List[List[Fraction]], 
                        fila_piv: int, col_piv: int, 
                        bases: List[str], variables: List[str]) -> None:
        """Realiza las operaciones de pivoteo en la tabla"""
        # Normalizar fila pivote
        pivote = tabla[fila_piv][col_piv]
        for j in range(len(tabla[fila_piv])):
            tabla[fila_piv][j] = tabla[fila_piv][j] / pivote
        
        # Eliminar en otras filas
        for i in range(len(tabla)):
            if i == fila_piv:
                continue
            factor = tabla[i][col_piv]
            for j in range(len(tabla[i])):
                tabla[i][j] = tabla[i][j] - factor * tabla[fila_piv][j]
        
        # Actualizar base
        bases[fila_piv] = variables[col_piv]

    def ejecutar_fase1(self, tabla: List[List[Fraction]], variables: List[str], 
                      n_vars: int) -> Tuple[bool, List[Dict[str, Any]], List[str]]:
        """Ejecuta las iteraciones de Fase 1"""
        iteraciones = []
        
        # Identificar bases iniciales
        bases = self.identificar_bases_iniciales(tabla, variables)
        
        # Guardar tabla inicial
        iteraciones.append({
            "headers": ["Base"] + variables + ["b"],
            "rows": self.tabla_a_formato_api(tabla, bases)
        })
        
        while True:
            col_piv, fila_piv = self.identificar_pivote_fase1(tabla, n_vars)
            
            if col_piv is None:
                # Óptimo alcanzado
                factible = tabla[0][-1] == 0  # Valor objetivo debe ser 0
                break
                
            if fila_piv is None:
                # Problema ilimitado (no factible)
                return False, iteraciones, bases
            
            # Realizar pivoteo
            self.realizar_pivoteo(tabla, fila_piv, col_piv, bases, variables)
            
            # Guardar iteración
            iteraciones.append({
                "headers": ["Base"] + variables + ["b"],
                "rows": self.tabla_a_formato_api(tabla, bases)
            })
        
        return factible, iteraciones, bases

    def construir_tabla_fase2(self, tabla_fase1: List[List[Fraction]], 
                             variables: List[str], artificiales: List[str], 
                             c: List[float]) -> Tuple[List[List[Fraction]], List[str], List[str]]:
        """Construye la tabla inicial de Fase 2"""
        # Filtrar variables artificiales
        idxs_art = [variables.index(a) for a in artificiales]
        idxs_vars = [i for i in range(len(variables)) if i not in idxs_art]
        variables_f2 = [variables[i] for i in idxs_vars]
        
        # Crear función objetivo de Fase 2
        c_f2 = [Fraction(c[i]).limit_denominator() if i < len(c) else Fraction(0) for i in idxs_vars]
        fila_z = [-coef for coef in c_f2] + [Fraction(0)]
        
        # Filtrar tabla
        tabla_f2 = [fila_z]
        for i, fila in enumerate(tabla_fase1[1:]):
            fila_filtrada = [fila[j] for j in idxs_vars] + [fila[-1]]
            tabla_f2.append(fila_filtrada)
        
        # Identificar bases en tabla filtrada
        bases_f2 = self.identificar_bases_fase2(tabla_f2, variables_f2)
        
        return tabla_f2, variables_f2, bases_f2

    def identificar_bases_iniciales(self, tabla: List[List[Fraction]], 
                                   variables: List[str]) -> List[str]:
        """Identifica las bases iniciales de la tabla"""
        bases = ["Z"]
        for i in range(1, len(tabla)):
            base_encontrada = "?"
            for j, var in enumerate(variables):
                # Verificar si la columna j es canónica para la fila i
                if (tabla[i][j] == 1 and 
                    all(tabla[k][j] == 0 for k in range(len(tabla)) if k != i)):
                    base_encontrada = var
                    break
            bases.append(base_encontrada)
        return bases

    def identificar_bases_fase2(self, tabla_f2: List[List[Fraction]], 
                               variables_f2: List[str]) -> List[str]:
        """Identifica bases para Fase 2 ignorando fila Z"""
        bases_f2 = ["Z"]
        for fila_idx in range(1, len(tabla_f2)):
            base_encontrada = "?"
            for j, var in enumerate(variables_f2):
                # Verificar canonicidad solo en filas de restricciones
                if (tabla_f2[fila_idx][j] == 1 and 
                    all(tabla_f2[k][j] == 0 for k in range(1, len(tabla_f2)) if k != fila_idx)):
                    base_encontrada = var
                    break
            bases_f2.append(base_encontrada)
        return bases_f2

    def canonizar_z_fase2(self, tabla_f2: List[List[Fraction]], 
                         bases_f2: List[str], variables_f2: List[str], 
                         n_vars: int) -> None:
        """Canoniza la fila Z para variables de decisión básicas"""
        for fila_idx, base in enumerate(bases_f2[1:], 1):
            if base in variables_f2[:n_vars]:  # Solo variables de decisión
                col_idx = variables_f2.index(base)
                # Verificar canonicidad (ignorando fila Z)
                es_canonica = (
                    tabla_f2[fila_idx][col_idx] == 1 and
                    all(tabla_f2[i][col_idx] == 0 for i in range(1, len(tabla_f2)) if i != fila_idx)
                )
                if es_canonica:
                    coef_z = tabla_f2[0][col_idx]
                    if coef_z != 0:
                        # Aplicar: Z <- Z - coef_z * fila_de_base
                        for j in range(len(tabla_f2[0])):
                            tabla_f2[0][j] = tabla_f2[0][j] - coef_z * tabla_f2[fila_idx][j]

    def ejecutar_fase2(self, tabla: List[List[Fraction]], variables: List[str], 
                      bases: List[str], objetivo: str) -> Tuple[bool, bool, List[Dict[str, Any]]]:
        """Ejecuta las iteraciones de Fase 2"""
        iteraciones = []
        
        # Guardar tabla inicial canonizada
        iteraciones.append({
            "headers": ["Base"] + variables + ["b"],
            "rows": self.tabla_a_formato_api(tabla, bases)
        })
        
        optimo = False
        ilimitado = False
        
        while True:
            col_piv, fila_piv = self.identificar_pivote_fase2(tabla, objetivo)
            
            if col_piv is None:
                # Óptimo alcanzado
                optimo = True
                break
                
            if fila_piv is None:
                # Solución ilimitada
                ilimitado = True
                break
            
            # Realizar pivoteo
            self.realizar_pivoteo(tabla, fila_piv, col_piv, bases, variables)
            
            # Guardar iteración
            iteraciones.append({
                "headers": ["Base"] + variables + ["b"],
                "rows": self.tabla_a_formato_api(tabla, bases)
            })
        
        return optimo, ilimitado, iteraciones

    def tabla_a_formato_api(self, tabla: List[List[Fraction]], 
                           bases: List[str]) -> List[List[Union[str, str]]]:
        """Convierte tabla a formato con fracciones como strings"""
        rows = []
        for i, (base, fila) in enumerate(zip(bases, tabla)):
            row = [base] + [self.fraction_to_string(val) for val in fila]
            rows.append(row)
        return rows

    def extraer_solucion_final(self, tabla: List[List[Fraction]], 
                              bases: List[str], variables: List[str], 
                              n_vars: int) -> Dict[str, str]:
        """Extrae la solución final como fracciones string"""
        solucion = {}
        
        # Inicializar variables de decisión en 0
        for i in range(n_vars):
            solucion[f"x{i+1}"] = "0"
        
        # Obtener valores de variables básicas
        for i, base in enumerate(bases[1:], 1):  # Saltar Z
            if base.startswith('x'):
                solucion[base] = self.fraction_to_string(tabla[i][-1])
        
        return solucion

    def solve_from_data(self, n_vars: int, n_cons: int, c: List[float], 
                       A: List[List[float]], b: List[float], signs: List[str], 
                       obj_type: str) -> Dict[str, Any]:
        """Resuelve el problema completo desde los datos de entrada"""
        try:
            self.n_vars_decision = n_vars
            self.objetivo_tipo = obj_type
            
            # Preparar ecuaciones
            variables, artificiales, filas_coef = self.preparar_ecuaciones(
                n_vars, n_cons, A, b, signs)
            
            self.variables = variables
            self.artificiales = artificiales
            
            # FASE 1
            tabla_fase1 = self.tabla_fase1_actualizada(variables, artificiales, filas_coef, b)
            factible, iteraciones_f1, bases_f1 = self.ejecutar_fase1(tabla_fase1, variables, n_vars)
            
            resultado = {
                "fase1": {
                    "factible": factible,
                    "valor_objetivo": self.fraction_to_string(tabla_fase1[0][-1]),
                    "iteraciones": iteraciones_f1
                }
            }
            
            if not factible:
                return resultado
            
            # FASE 2
            tabla_f2, variables_f2, bases_f2 = self.construir_tabla_fase2(
                tabla_fase1, variables, artificiales, c)
            
            # Canonizar Z
            self.canonizar_z_fase2(tabla_f2, bases_f2, variables_f2, n_vars)
            
            # Ejecutar iteraciones de Fase 2
            optimo, ilimitado, iteraciones_f2 = self.ejecutar_fase2(
                tabla_f2, variables_f2, bases_f2, obj_type)
            
            # Extraer solución final
            solucion_final = self.extraer_solucion_final(tabla_f2, bases_f2, variables_f2, n_vars)
            
            resultado["fase2"] = {
                "optimo": optimo,
                "ilimitado": ilimitado,
                "valor_objetivo": self.fraction_to_string(tabla_f2[0][-1]),
                "solucion": solucion_final,
                "iteraciones": iteraciones_f2
            }
            
            return resultado
            
        except Exception as e:
            return {"error": f"Error en solve_from_data: {str(e)}"}


# Clase para compatibilidad con API existente
class SimplexDosFasesTablaCompleta(SimplexCompleto):
    """Clase wrapper para mantener compatibilidad con API existente"""
    pass

def resolver_dos_fases_frontend(n_vars: int, n_cons: int, c: List[float], A: List[List[float]], b: List[float], signos: List[str], objetivo: str) -> Dict[str, Any]:
    """
    Función adaptada para el frontend/backend: recibe los datos del problema y retorna el resultado del método de dos fases.
    """
    solver = SimplexDosFasesTablaCompleta()
    resultado = solver.solve_from_data(
        n_vars=n_vars,
        n_cons=n_cons,
        c=c,
        A=A,
        b=b,
        signs=signos,
        obj_type=objetivo
    )
    return resultado