#!/usr/bin/env python3
"""
Test detallado para analizar paso a paso el método Dos Fases
y encontrar por qué no se detiene en el momento correcto.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'components'))

from Metodo2F import SimplexDosFases

def analyze_dos_fases_detailed():
    """
    Análisis detallado del método Dos Fases.
    """
    print("🔍 ANÁLISIS DETALLADO DEL MÉTODO DOS FASES")
    print("=" * 60)
    
    # Datos del problema
    sm = SimplexDosFases()
    
    result = sm.solve_from_data(
        n_vars=4,
        n_cons=4,
        c=[3, 4, 2, 5],
        A=[
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1]
        ],
        b=[100, 80, 70, 110],
        signs=["<=", "<=", ">=", ">="],
        obj_type="min"
    )
    
    print("\n📊 FASE I - RESUMEN:")
    print(f"Factible: {result['fase1']['factible']}")
    print(f"Valor objetivo Fase I: {result['fase1']['valor_objetivo']}")
    print(f"Iteraciones: {len(result['fase1']['iteraciones'])}")
    
    # Mostrar tabla final de Fase I
    if result['fase1']['iteraciones']:
        tabla_final_f1 = result['fase1']['iteraciones'][-1]['tabla']
        print("\n📋 TABLA FINAL FASE I:")
        print(f"Headers: {tabla_final_f1['headers']}")
        for row in tabla_final_f1['rows']:
            print(f"{row['base']}: {row['values']}")
    
    print("\n" + "=" * 60)
    print("📊 FASE II - ANÁLISIS DETALLADO:")
    
    if result['fase2']:
        print(f"Iteraciones ejecutadas: {len(result['fase2']['iteraciones'])}")
        
        for i, iteracion in enumerate(result['fase2']['iteraciones']):
            print(f"\n--- ITERACIÓN {iteracion['paso']} ---")
            tabla = iteracion['tabla']
            
            # Mostrar toda la tabla
            print("Headers:", tabla['headers'])
            for row in tabla['rows']:
                print(f"{row['base']:>4}: {row['values']}")
            
            # Analizar fila objetivo
            fila_obj = tabla['rows'][0]['values']
            print(f"\n🎯 Análisis fila objetivo:")
            print(f"Valores: {fila_obj}")
            
            # Contar valores negativos
            negativos = [v for v in fila_obj[:-1] if v < -1e-8]
            print(f"Valores negativos: {negativos}")
            print(f"Cantidad de negativos: {len(negativos)}")
            
            if len(negativos) == 0:
                print("✅ NO HAY NEGATIVOS - DEBERÍA SER ÓPTIMA")
            else:
                print(f"⏳ Hay {len(negativos)} negativos - debe continuar")
            
            # Verificar si es óptima
            if iteracion.get('optima', False):
                print("✅ MARCADA COMO ÓPTIMA")
                break
            else:
                print("❌ NO marcada como óptima")
        
        # Mostrar resultado final
        if 'solucion' in result['fase2']:
            print(f"\n🏆 RESULTADO FINAL:")
            print(f"Valor objetivo: {result['fase2']['valor_objetivo']}")
            print("Variables:")
            for var, valor in result['fase2']['solucion'].items():
                print(f"  {var} = {valor}")
    
    print("\n" + "=" * 60)
    print("💡 ANÁLISIS:")
    
    # Calcular cuántas iteraciones deberían ser necesarias
    expected_iterations = 1  # Según la imagen del usuario
    actual_iterations = len(result['fase2']['iteraciones'])
    
    if actual_iterations == expected_iterations:
        print(f"✅ PERFECTO: {actual_iterations} iteración(es) como esperado")
    else:
        print(f"❌ PROBLEMA: {actual_iterations} iteraciones vs {expected_iterations} esperada(s)")
        print("🔧 Posibles causas:")
        print("  - Tabla inicial de Fase II no está bien construida")
        print("  - Criterio de optimalidad incorrecto")
        print("  - Problema en el pivoteo")

if __name__ == "__main__":
    analyze_dos_fases_detailed()
