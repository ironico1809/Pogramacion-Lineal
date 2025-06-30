#!/usr/bin/env python3
"""
Corrección del método _ejecutar_fase2 basada en el análisis manual
"""

def _ejecutar_fase2_corrected(self, fase1_result):
    """
    Versión corregida de la Fase II del método Dos Fases
    """
    # Obtener la tabla final de la Fase I
    tabla_fase1_final = fase1_result["tabla_final"]
    base_vars_fase1 = fase1_result["base_vars"]
    
    # Construir tabla inicial para Fase II
    # 1. Eliminar columnas de variables artificiales
    var_names_fase2 = [var for var in self.var_names if not var.startswith('a')]
    
    # 2. Construir fila objetivo original
    obj_row_fase2 = []
    for var in var_names_fase2:
        if var.startswith('x'):
            idx = int(var[1:]) - 1  # x1 -> índice 0
            if self.original_obj_type == "min":
                obj_row_fase2.append(-self.c[idx])  # Para maximización
            else:
                obj_row_fase2.append(self.c[idx])
        else:
            obj_row_fase2.append(0)  # Variables de holgura/exceso
    obj_row_fase2.append(0)  # RHS inicial
    
    # 3. Copiar filas de restricciones (sin columnas artificiales)
    tableau_fase2 = [obj_row_fase2]
    base_vars_fase2 = []
    
    for i, base_var in enumerate(base_vars_fase1):
        if not base_var.startswith('a'):  # Solo variables no artificiales
            fila_original = tabla_fase1_final[i + 1]
            fila_nueva = []
            
            # Copiar solo columnas de variables no artificiales
            for j, var in enumerate(self.var_names):
                if not var.startswith('a'):
                    fila_nueva.append(fila_original[j])
            
            fila_nueva.append(fila_original[-1])  # RHS
            tableau_fase2.append(fila_nueva)
            base_vars_fase2.append(base_var)
    
    # 4. Eliminar variables básicas de la función objetivo
    for i, base_var in enumerate(base_vars_fase2):
        if base_var.startswith('x'):
            # Encontrar índice de la variable en var_names_fase2
            j = var_names_fase2.index(base_var)
            
            # Eliminar variable básica de la función objetivo
            coef = tableau_fase2[0][j]
            if abs(coef) > 1e-8:
                # Realizar operación fila: R0 = R0 - coef * Ri
                for k in range(len(tableau_fase2[0])):
                    tableau_fase2[0][k] -= coef * tableau_fase2[i + 1][k]
    
    # 5. Ejecutar iteraciones de Fase II
    iteraciones_fase2 = []
    paso = 1
    max_iteraciones = 20
    
    while paso <= max_iteraciones:
        # Guardar iteración actual
        iteracion = {
            "paso": paso,
            "tabla": self._serialize_tableau_simple(tableau_fase2, base_vars_fase2, var_names_fase2),
            "base": base_vars_fase2.copy()
        }
        iteraciones_fase2.append(iteracion)
        
        # Buscar columna pivote (más negativa)
        j_pivot = None
        min_val = 0
        
        for j in range(len(tableau_fase2[0]) - 1):
            val = tableau_fase2[0][j]
            if val < min_val:
                min_val = val
                j_pivot = j
        
        # Criterio de optimalidad
        if j_pivot is None or min_val >= -1e-8:
            # Solución óptima encontrada
            iteracion["optima"] = True
            
            # Calcular resultado final
            variables_solucion = {var: 0 for var in self.var_names[:self.n_vars]}
            for i, base_var in enumerate(base_vars_fase2):
                if base_var in variables_solucion:
                    variables_solucion[base_var] = tableau_fase2[i + 1][-1]
            
            valor_objetivo = -tableau_fase2[0][-1]  # Cambiar signo para minimización
            
            iteracion["solucion_final"] = {
                "variables": variables_solucion,
                "valor_objetivo": valor_objetivo
            }
            break
        
        # Buscar fila pivote (prueba de la razón)
        min_ratio = None
        i_pivot = None
        for i in range(1, len(tableau_fase2)):
            if tableau_fase2[i][j_pivot] > 0:
                ratio = tableau_fase2[i][-1] / tableau_fase2[i][j_pivot]
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                    i_pivot = i
        
        if i_pivot is None:
            # Problema ilimitado
            iteracion["ilimitado"] = True
            break
        
        # Realizar operaciones de pivoteo
        tableau_fase2 = self._pivot_operation_simple(tableau_fase2, i_pivot, j_pivot)
        base_vars_fase2[i_pivot - 1] = var_names_fase2[j_pivot]
        paso += 1
    
    # Procesar resultado final
    resultado_fase2 = {"iteraciones": iteraciones_fase2}
    
    if iteraciones_fase2 and iteraciones_fase2[-1].get("optima"):
        ultima_iteracion = iteraciones_fase2[-1]
        if "solucion_final" in ultima_iteracion:
            solucion_info = ultima_iteracion["solucion_final"]
            resultado_fase2.update({
                "optimo": True,
                "solucion": solucion_info["variables"],
                "valor_objetivo": solucion_info["valor_objetivo"]
            })
    
    return resultado_fase2

def _serialize_tableau_simple(self, tableau, base_vars, var_names):
    """Serializar tabla de manera simple"""
    headers = ["Base"] + var_names + ["b"]
    rows = []
    
    # Fila objetivo
    rows.append({"base": "-Z", "values": tableau[0]})
    
    # Filas de restricciones
    for i, base_var in enumerate(base_vars):
        rows.append({"base": base_var, "values": tableau[i + 1]})
    
    return {"headers": headers, "rows": rows}

def _pivot_operation_simple(self, tableau, i_pivot, j_pivot):
    """Operación de pivoteo simplificada"""
    pivot = tableau[i_pivot][j_pivot]
    
    # Normalizar fila pivote
    for j in range(len(tableau[i_pivot])):
        tableau[i_pivot][j] /= pivot
    
    # Eliminar columna pivote en otras filas
    for i in range(len(tableau)):
        if i != i_pivot:
            factor = tableau[i][j_pivot]
            for j in range(len(tableau[i])):
                tableau[i][j] -= factor * tableau[i_pivot][j]
    
    return tableau

print("✅ Código de corrección creado")
print("Este código debe reemplazar el método _ejecutar_fase2 existente")
