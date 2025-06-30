from fractions import Fraction

def analisis_manual_problema():
    """Análisis manual paso a paso del problema para encontrar el error."""
    
    print("=== ANÁLISIS MANUAL DEL PROBLEMA ===")
    print("Problema: Minimizar Z = 2000x1 + 500x2")
    print("Restricciones:")
    print("  2x1 + 3x2 >= 36")
    print("  3x1 + 6x2 >= 60")
    print("  x1, x2 >= 0")
    print()
    
    # Variables originales: x1, x2
    # Variables de exceso: e1, e2 (para >=)
    # Variables artificiales: a1, a2
    
    print("=== CONSTRUCCIÓN TABLA INICIAL FASE I ===")
    print("Variables: x1, x2, e1, e2, a1, a2")
    print("Base inicial: [a1, a2]")
    print()
    
    # Tabla inicial antes de ajustar fila objetivo
    print("Tabla inicial (antes de ajustar fila objetivo):")
    print("     | x1  x2  e1  e2  a1  a2 | b")
    print("-----|------------------------|---")
    print("  W  |  0   0   0   0   1   1 | 0   <- Fila objetivo Fase I")
    print(" a1  |  2   3  -1   0   1   0 | 36  <- 2x1 + 3x2 - e1 + a1 = 36")
    print(" a2  |  3   6   0  -1   0   1 | 60  <- 3x1 + 6x2 - e2 + a2 = 60")
    print()
    
    # Ajustar fila objetivo restando filas artificiales
    print("Ajustando fila objetivo (W = W - a1_row - a2_row):")
    print("W = [0,0,0,0,1,1,0] - [2,3,-1,0,1,0,36] - [3,6,0,-1,0,1,60]")
    print("W = [0-2-3, 0-3-6, 0-(-1)-0, 0-0-(-1), 1-1-0, 1-0-1, 0-36-60]")
    print("W = [-5, -9, 1, 1, 0, 0, -96]")
    print()
    
    print("Tabla ajustada Fase I:")
    print("     | x1  x2  e1  e2  a1  a2 | b")
    print("-----|------------------------|---")
    print("  W  | -5  -9   1   1   0   0 |-96")
    print(" a1  |  2   3  -1   0   1   0 | 36")
    print(" a2  |  3   6   0  -1   0   1 | 60")
    print()
    
    print("=== ITERACIONES FASE I ===")
    print("Buscamos el valor más positivo en la fila W para la columna pivote.")
    print("Los valores positivos son: e1=1, e2=1")
    print("Elegimos e1 (columna 2, índice desde 0) o e2 (columna 3)")
    print()
    
    print("Si elegimos e1 como columna pivote:")
    print("Ratios: a1: -1 (negativo, no válido), a2: 0 (no válido)")
    print("Si elegimos e2 como columna pivote:")
    print("Ratios: a1: 0 (no válido), a2: -1 (negativo, no válido)")
    print()
    print("¡PROBLEMA ENCONTRADO!")
    print("Las variables de exceso tienen coeficientes negativos en las restricciones,")
    print("lo que hace que no se puedan usar como pivote en la Fase I.")
    print()
    
    print("=== ANÁLISIS DEL PROBLEMA ===")
    print("El problema está en la construcción de la tabla.")
    print("Para restricciones >=, la forma estándar es:")
    print("  ax + by - s + a = c")
    print("donde s es variable de exceso (coef. -1) y a es artificial (coef. +1)")
    print()
    print("Pero esto crea un problema en Fase I porque las variables de exceso")
    print("no pueden ser pivote (tienen coeficientes negativos).")
    print()
    
    print("=== SOLUCIÓN ===")
    print("El problema real es que necesitamos reformular como:")
    print("  ax + by >= c")
    print("  ax + by - s = c  (donde s <= 0, por lo que -s >= 0)")
    print("  ax + by + s' = c  (donde s' = -s >= 0)")
    print()
    print("O usar directamente variables artificiales sin exceso para >=")

def analisis_gran_m_vs_dos_fases():
    """Comparar por qué Gran M funciona pero Dos Fases no."""
    print("\n=== COMPARACIÓN GRAN M vs DOS FASES ===")
    print()
    print("GRAN M:")
    print("- Usa una sola fase")
    print("- Penaliza variables artificiales con M grande")
    print("- La tabla mantiene todas las variables todo el tiempo")
    print("- No hay transición problemática entre fases")
    print()
    print("DOS FASES:")
    print("- Fase I: elimina variables artificiales")  
    print("- Fase II: optimiza función original")
    print("- Debe reconstruir la tabla eliminando artificiales")
    print("- La transición puede causar problemas con variables de exceso")
    print()
    print("EL PROBLEMA:")
    print("En Dos Fases, cuando eliminamos variables artificiales,")
    print("las variables de exceso pueden quedar 'mal configuradas'")
    print("en la nueva base, causando que el algoritmo detecte")
    print("falsamente que el problema es ilimitado.")

if __name__ == "__main__":
    analisis_manual_problema()
    analisis_gran_m_vs_dos_fases()
