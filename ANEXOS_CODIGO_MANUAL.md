# ANEXOS

## Anexo A: Código del Programa

### A.1 Estructura del Proyecto

```
Project/
├── src/
│   ├── App.tsx                    # Componente principal de React
│   ├── main.tsx                   # Punto de entrada de React
│   ├── index.css                  # Estilos globales
│   ├── api/
│   │   └── simplex.ts            # Cliente API para comunicación con backend
│   ├── components/
│   │   ├── TransportSolver.tsx    # Componente principal del solver
│   │   ├── MetodoM.py            # Implementación método Gran M
│   │   └── Metodo2F.py           # Implementación método Dos Fases
│   └── assets/
├── public/
├── package.json                   # Dependencias del proyecto
├── vite.config.ts                # Configuración de Vite
├── tsconfig.json                 # Configuración de TypeScript
└── python_wrapper.py            # Wrapper para ejecutar Python desde Node.js
```

### A.2 Código Frontend (React + TypeScript)

#### A.2.1 Componente Principal - App.tsx

```typescript
/**
 * SISTEMA DE OPTIMIZACIÓN DE TRANSPORTE
 * Componente principal de la aplicación React
 * 
 * Funcionalidades:
 * - Interfaz de usuario para problemas de transporte
 * - Integración con backend Python (Gran M y Dos Fases)
 * - Visualización de resultados y iteraciones
 * 
 * @author Equipo de Desarrollo
 * @version 1.0
 */

import React from 'react';
import TransportSolver from './components/TransportSolver';
import './App.css';

/**
 * Componente raíz de la aplicación
 * Renderiza el solver de transporte principal
 */
function App() {
  return (
    <div className="App">
      {/* Header principal de la aplicación */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-6">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold text-center">
            Sistema de Optimización de Transporte
          </h1>
          <p className="text-center mt-2 opacity-90">
            Métodos Simplex: Gran M y Dos Fases
          </p>
        </div>
      </header>

      {/* Contenido principal */}
      <main className="min-h-screen bg-gray-50">
        <TransportSolver />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-4">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2025 Sistema de Optimización de Transporte</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
```

#### A.2.2 Cliente API - api/simplex.ts

```typescript
/**
 * CLIENTE API PARA COMUNICACIÓN CON BACKEND PYTHON
 * 
 * Maneja todas las comunicaciones HTTP entre el frontend React
 * y el backend Python que implementa los algoritmos Simplex
 * 
 * Características:
 * - Manejo de errores robusto
 * - Timeout configurable
 * - Validación de datos
 * - Logging de operaciones
 */

// Interfaces para tipado TypeScript
export interface TransportProblem {
  method: 'gran_m' | 'dos_fases';
  optimization_type: 'minimize' | 'maximize';
  num_origins: number;
  num_destinations: number;
  cost_matrix: number[][];
  supply: number[];
  demand: number[];
}

export interface SimplexIteration {
  iteration: number;
  tableau: number[][];
  basic_vars: string[];
  entering_var: string;
  leaving_var: string;
  pivot_element: number;
  is_optimal: boolean;
  ratios?: number[];
}

export interface SolutionResult {
  status: 'optimal' | 'infeasible' | 'unbounded' | 'error';
  method_used: string;
  optimal_value: number;
  solution_matrix: number[][];
  basic_variables: string[];
  iterations: SimplexIteration[];
  interpretation: string;
  execution_time: number;
  total_iterations: number;
}

/**
 * Configuración de la API
 */
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  TIMEOUT: 30000, // 30 segundos
  HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

/**
 * Clase principal para comunicación con la API
 */
export class SimplexAPI {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = API_CONFIG.BASE_URL, timeout: number = API_CONFIG.TIMEOUT) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
  }

  /**
   * Resuelve un problema de transporte usando el método especificado
   * 
   * @param problem - Datos del problema de transporte
   * @returns Promise con la solución del problema
   * @throws Error si hay problemas de comunicación o datos inválidos
   */
  async solveProblem(problem: TransportProblem): Promise<SolutionResult> {
    try {
      // Validar datos de entrada
      this.validateProblem(problem);
      
      console.log('📤 Enviando problema al backend:', {
        method: problem.method,
        dimensions: `${problem.num_origins}x${problem.num_destinations}`,
        optimization: problem.optimization_type
      });

      // Configurar timeout para la petición
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      // Realizar petición HTTP
      const response = await fetch(`${this.baseUrl}/solve`, {
        method: 'POST',
        headers: API_CONFIG.HEADERS,
        body: JSON.stringify(problem),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Verificar respuesta HTTP
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Error del servidor'}`);
      }

      // Procesar respuesta exitosa
      const result: SolutionResult = await response.json();
      
      console.log('📥 Respuesta del backend recibida:', {
        status: result.status,
        iterations: result.total_iterations,
        optimal_value: result.optimal_value,
        execution_time: `${result.execution_time}ms`
      });

      return result;

    } catch (error) {
      console.error('❌ Error en comunicación con API:', error);
      
      // Manejo específico de diferentes tipos de errores
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('No se puede conectar con el servidor. Verifique que el backend esté ejecutándose.');
      }
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('La operación tardó demasiado tiempo. Intente con un problema más pequeño.');
      }
      
      throw error;
    }
  }

  /**
   * Valida los datos del problema antes de enviarlos
   * 
   * @param problem - Problema a validar
   * @throws Error si los datos son inválidos
   */
  private validateProblem(problem: TransportProblem): void {
    // Validar dimensiones
    if (problem.num_origins < 1 || problem.num_origins > 10) {
      throw new Error('El número de orígenes debe estar entre 1 y 10');
    }
    
    if (problem.num_destinations < 1 || problem.num_destinations > 10) {
      throw new Error('El número de destinos debe estar entre 1 y 10');
    }

    // Validar matriz de costos
    if (!Array.isArray(problem.cost_matrix) || 
        problem.cost_matrix.length !== problem.num_origins) {
      throw new Error('La matriz de costos debe tener las dimensiones correctas');
    }

    problem.cost_matrix.forEach((row, i) => {
      if (!Array.isArray(row) || row.length !== problem.num_destinations) {
        throw new Error(`La fila ${i + 1} de la matriz de costos es inválida`);
      }
      
      row.forEach((cost, j) => {
        if (typeof cost !== 'number' || cost < 0) {
          throw new Error(`El costo en posición [${i + 1}, ${j + 1}] debe ser un número positivo`);
        }
      });
    });

    // Validar vectores de oferta y demanda
    if (problem.supply.length !== problem.num_origins) {
      throw new Error('El vector de oferta debe tener la misma longitud que el número de orígenes');
    }
    
    if (problem.demand.length !== problem.num_destinations) {
      throw new Error('El vector de demanda debe tener la misma longitud que el número de destinos');
    }

    // Validar valores positivos
    problem.supply.forEach((supply, i) => {
      if (typeof supply !== 'number' || supply <= 0) {
        throw new Error(`La oferta del origen ${i + 1} debe ser un número positivo`);
      }
    });

    problem.demand.forEach((demand, i) => {
      if (typeof demand !== 'number' || demand <= 0) {
        throw new Error(`La demanda del destino ${i + 1} debe ser un número positivo`);
      }
    });
  }

  /**
   * Verifica si el servidor backend está disponible
   * 
   * @returns Promise<boolean> - true si el servidor responde
   */
  async checkServerHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Instancia por defecto de la API
export const simplexAPI = new SimplexAPI();

/**
 * Función de conveniencia para resolver problemas
 * 
 * @param problem - Problema de transporte
 * @returns Promise con la solución
 */
export const solveProblem = (problem: TransportProblem): Promise<SolutionResult> => {
  return simplexAPI.solveProblem(problem);
};

/**
 * Función para verificar estado del servidor
 * 
 * @returns Promise<boolean> - Estado del servidor
 */
export const checkServerStatus = (): Promise<boolean> => {
  return simplexAPI.checkServerHealth();
};
```

### A.3 Código Backend (Python)

#### A.3.1 Método Gran M - components/MetodoM.py

```python
"""
IMPLEMENTACIÓN DEL MÉTODO DE LA GRAN M PARA PROBLEMAS DE TRANSPORTE

Este módulo implementa el algoritmo Simplex usando el método de la Gran M
para resolver problemas de programación lineal con variables artificiales.

Características principales:
- Manejo de variables artificiales con penalización M
- Detección de infactibilidad
- Registro completo de iteraciones
- Aritmética de fracciones para precisión numérica

Autor: Equipo de Desarrollo
Versión: 2.0
Fecha: 2025
"""

from fractions import Fraction
from typing import List, Dict, Any, Tuple, Optional
import json
import sys

class GranMSolver:
    """
    Solver para el método de la Gran M
    
    Atributos:
        M (int): Valor de la gran M (penalización)
        tabla (List[List[Fraction]]): Tabla simplex actual
        variables_basicas (List[str]): Variables en la base actual
        variables_artificiales (List[str]): Variables artificiales del problema
        iteraciones (List[Dict]): Historial de todas las iteraciones
        num_iteracion (int): Contador de iteraciones
    """
    
    def __init__(self, M: int = 1000):
        """
        Inicializa el solver con el valor de M especificado
        
        Args:
            M (int): Valor de la gran M para penalización
        """
        self.M = M
        self.tabla = []
        self.variables_basicas = []
        self.variables_artificiales = []
        self.iteraciones = []
        self.num_iteracion = 0
        
    def resolver_gran_m(self, costos: List[List[float]], 
                       ofertas: List[float], 
                       demandas: List[float], 
                       tipo_optimizacion: str = "minimize") -> Dict[str, Any]:
        """
        Resuelve un problema de transporte usando el método de la Gran M
        
        Args:
            costos: Matriz de costos de transporte (m x n)
            ofertas: Vector de capacidades de los orígenes (m x 1)
            demandas: Vector de demandas de los destinos (n x 1)
            tipo_optimizacion: "minimize" o "maximize"
            
        Returns:
            Dict con la solución completa del problema
            
        Raises:
            ValueError: Si los datos de entrada son inválidos
            RuntimeError: Si el algoritmo no converge
        """
        try:
            # Validar y preparar datos
            self._validar_datos(costos, ofertas, demandas)
            
            # Convertir a problema de minimización si es necesario
            if tipo_optimizacion == "maximize":
                costos = [[-c for c in fila] for fila in costos]
            
            # Balancear el problema (agregar variable ficticia si es necesario)
            costos_balanceados, ofertas_balanceadas, demandas_balanceadas = \
                self._balancear_problema(costos, ofertas, demandas)
            
            # Construir tabla inicial
            self._construir_tabla_inicial(costos_balanceados, ofertas_balanceadas, demandas_balanceadas)
            
            # Algoritmo iterativo Simplex
            while not self._es_optimo():
                self.num_iteracion += 1
                
                # Registrar iteración actual
                self._registrar_iteracion()
                
                # Seleccionar variable entrante (más negativa en fila Z)
                columna_entrante = self._seleccionar_variable_entrante()
                if columna_entrante == -1:
                    break
                    
                # Prueba de la razón mínima
                fila_saliente = self._prueba_razon_minima(columna_entrante)
                if fila_saliente == -1:
                    return self._resultado_no_acotado()
                
                # Realizar pivoteo
                self._realizar_pivoteo(fila_saliente, columna_entrante)
                
                # Verificar límite de iteraciones (prevenir ciclos infinitos)
                if self.num_iteracion > 100:
                    raise RuntimeError("Demasiadas iteraciones - posible ciclo infinito")
            
            # Registrar iteración final
            self._registrar_iteracion(es_final=True)
            
            # Verificar factibilidad
            if self._hay_variables_artificiales_en_base():
                return self._resultado_infactible()
            
            # Construir y retornar solución
            return self._construir_solucion_final(len(costos), len(costos[0]), tipo_optimizacion)
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "iterations": self.iteraciones
            }
    
    def _validar_datos(self, costos: List[List[float]], 
                      ofertas: List[float], 
                      demandas: List[float]) -> None:
        """
        Valida que los datos de entrada sean consistentes
        
        Args:
            costos: Matriz de costos
            ofertas: Vector de ofertas
            demandas: Vector de demandas
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not costos or not ofertas or not demandas:
            raise ValueError("Los datos no pueden estar vacíos")
        
        m, n = len(costos), len(costos[0])
        
        if len(ofertas) != m:
            raise ValueError(f"Vector de ofertas debe tener {m} elementos")
        
        if len(demandas) != n:
            raise ValueError(f"Vector de demandas debe tener {n} elementos")
        
        # Verificar que todos los costos sean no negativos
        for i, fila in enumerate(costos):
            if len(fila) != n:
                raise ValueError(f"Fila {i} de costos tiene dimensión incorrecta")
            for j, costo in enumerate(fila):
                if costo < 0:
                    raise ValueError(f"Costo en posición [{i}][{j}] es negativo")
        
        # Verificar que ofertas y demandas sean positivas
        for i, oferta in enumerate(ofertas):
            if oferta <= 0:
                raise ValueError(f"Oferta {i} debe ser positiva")
        
        for i, demanda in enumerate(demandas):
            if demanda <= 0:
                raise ValueError(f"Demanda {i} debe ser positiva")
    
    def _balancear_problema(self, costos: List[List[float]], 
                           ofertas: List[float], 
                           demandas: List[float]) -> Tuple[List[List[float]], List[float], List[float]]:
        """
        Balancea el problema agregando origen o destino ficticio si es necesario
        
        Args:
            costos: Matriz de costos original
            ofertas: Vector de ofertas original
            demandas: Vector de demandas original
            
        Returns:
            Tupla con costos, ofertas y demandas balanceados
        """
        total_oferta = sum(ofertas)
        total_demanda = sum(demandas)
        
        costos_bal = [fila[:] for fila in costos]  # Copia profunda
        ofertas_bal = ofertas[:]
        demandas_bal = demandas[:]
        
        if total_oferta > total_demanda:
            # Agregar destino ficticio
            diferencia = total_oferta - total_demanda
            for fila in costos_bal:
                fila.append(0)  # Costo cero para destino ficticio
            demandas_bal.append(diferencia)
            
        elif total_demanda > total_oferta:
            # Agregar origen ficticio
            diferencia = total_demanda - total_oferta
            costos_bal.append([0] * len(demandas_bal))  # Fila de costos cero
            ofertas_bal.append(diferencia)
        
        return costos_bal, ofertas_bal, demandas_bal
    
    def _construir_tabla_inicial(self, costos: List[List[float]], 
                                ofertas: List[float], 
                                demandas: List[float]) -> None:
        """
        Construye la tabla inicial del método Gran M
        
        La tabla incluye:
        - Variables de decisión (xij)
        - Variables de holgura para restricciones de oferta
        - Variables artificiales para restricciones de demanda
        - Función objetivo con penalización M
        """
        m, n = len(costos), len(costos[0])
        
        # Calcular número total de variables
        num_vars_decision = m * n
        num_vars_holgura = m  # Una por cada restricción de oferta
        num_vars_artificiales = n  # Una por cada restricción de demanda
        total_vars = num_vars_decision + num_vars_holgura + num_vars_artificiales
        
        # Inicializar tabla (m + n + 1 filas, total_vars + 1 columnas)
        num_filas = m + n + 1
        num_columnas = total_vars + 1
        self.tabla = [[Fraction(0)] * num_columnas for _ in range(num_filas)]
        
        # Construir restricciones de oferta
        for i in range(m):
            # Coeficientes de variables de decisión
            for j in range(n):
                self.tabla[i][i * n + j] = Fraction(1)
            
            # Variable de holgura
            self.tabla[i][num_vars_decision + i] = Fraction(1)
            
            # Lado derecho (RHS)
            self.tabla[i][-1] = Fraction(ofertas[i])
        
        # Construir restricciones de demanda
        for j in range(n):
            fila = m + j
            
            # Coeficientes de variables de decisión
            for i in range(m):
                self.tabla[fila][i * n + j] = Fraction(1)
            
            # Variable artificial
            self.tabla[fila][num_vars_decision + num_vars_holgura + j] = Fraction(1)
            
            # Lado derecho (RHS)
            self.tabla[fila][-1] = Fraction(demandas[j])
        
        # Construir función objetivo (fila Z)
        fila_z = num_filas - 1
        
        # Coeficientes de variables de decisión
        for i in range(m):
            for j in range(n):
                self.tabla[fila_z][i * n + j] = Fraction(costos[i][j])
        
        # Coeficientes de variables artificiales (penalización M)
        for j in range(n):
            self.tabla[fila_z][num_vars_decision + num_vars_holgura + j] = Fraction(self.M)
        
        # Inicializar variables básicas (variables artificiales)
        self.variables_basicas = []
        self.variables_artificiales = []
        
        # Variables básicas iniciales: holguras de oferta
        for i in range(m):
            self.variables_basicas.append(f"s{i+1}")
        
        # Variables básicas iniciales: artificiales de demanda
        for j in range(n):
            var_artificial = f"a{j+1}"
            self.variables_basicas.append(var_artificial)
            self.variables_artificiales.append(var_artificial)
        
        # Eliminar M de la fila objetivo (hacer variables artificiales no básicas)
        self._eliminar_M_fila_objetivo()
    
    def _eliminar_M_fila_objetivo(self) -> None:
        """
        Elimina el coeficiente M de la fila objetivo para las variables artificiales básicas
        Esto se hace restando M veces cada fila de restricción que tiene variable artificial
        """
        m = len([v for v in self.variables_basicas if v.startswith('s')])
        n = len([v for v in self.variables_basicas if v.startswith('a')])
        fila_z = len(self.tabla) - 1
        
        # Para cada variable artificial en la base
        for j in range(n):
            fila_restriccion = m + j
            # Restar M veces la fila de restricción de la fila Z
            for col in range(len(self.tabla[0])):
                self.tabla[fila_z][col] -= Fraction(self.M) * self.tabla[fila_restriccion][col]
    
    def _es_optimo(self) -> bool:
        """
        Verifica si la solución actual es óptima
        
        Returns:
            bool: True si es óptima (todos los coeficientes en fila Z son no negativos)
        """
        fila_z = len(self.tabla) - 1
        
        # Verificar todos los coeficientes excepto el RHS
        for j in range(len(self.tabla[0]) - 1):
            if self.tabla[fila_z][j] < -Fraction(1, 1000000):  # Tolerancia numérica
                return False
        
        return True
    
    def _seleccionar_variable_entrante(self) -> int:
        """
        Selecciona la variable que entra a la base (más negativa en fila Z)
        
        Returns:
            int: Índice de la columna de la variable entrante, -1 si es óptima
        """
        fila_z = len(self.tabla) - 1
        min_valor = Fraction(0)
        columna_entrante = -1
        
        for j in range(len(self.tabla[0]) - 1):
            if self.tabla[fila_z][j] < min_valor:
                min_valor = self.tabla[fila_z][j]
                columna_entrante = j
        
        return columna_entrante
    
    def _prueba_razon_minima(self, columna_entrante: int) -> int:
        """
        Encuentra la variable que sale de la base usando la prueba de la razón mínima
        
        Args:
            columna_entrante: Índice de la columna de la variable entrante
            
        Returns:
            int: Índice de la fila de la variable saliente, -1 si es no acotado
        """
        min_ratio = None
        fila_saliente = -1
        
        # Examinar todas las filas excepto la fila Z
        for i in range(len(self.tabla) - 1):
            elemento_pivote = self.tabla[i][columna_entrante]
            
            if elemento_pivote > Fraction(0):  # Solo ratios positivos
                ratio = self.tabla[i][-1] / elemento_pivote
                
                if min_ratio is None or ratio < min_ratio:
                    min_ratio = ratio
                    fila_saliente = i
        
        return fila_saliente
    
    def _realizar_pivoteo(self, fila_pivote: int, columna_pivote: int) -> None:
        """
        Realiza el pivoteo de Gauss-Jordan en la tabla
        
        Args:
            fila_pivote: Fila del elemento pivote
            columna_pivote: Columna del elemento pivote
        """
        elemento_pivote = self.tabla[fila_pivote][columna_pivote]
        
        # Normalizar fila pivote
        for j in range(len(self.tabla[0])):
            self.tabla[fila_pivote][j] /= elemento_pivote
        
        # Eliminar columna pivote en otras filas
        for i in range(len(self.tabla)):
            if i != fila_pivote:
                multiplicador = self.tabla[i][columna_pivote]
                for j in range(len(self.tabla[0])):
                    self.tabla[i][j] -= multiplicador * self.tabla[fila_pivote][j]
        
        # Actualizar variable básica
        self.variables_basicas[fila_pivote] = self._obtener_nombre_variable(columna_pivote)
    
    def _obtener_nombre_variable(self, columna: int) -> str:
        """
        Obtiene el nombre de la variable correspondiente a una columna
        
        Args:
            columna: Índice de la columna
            
        Returns:
            str: Nombre de la variable
        """
        # Determinar dimensiones del problema original
        m = len([v for v in self.variables_basicas if v.startswith('s')])
        n = len([v for v in self.variables_basicas if v.startswith('a')])
        
        if m == 0:  # Calcular desde la tabla
            m = len(self.tabla) - 1 - n
        
        num_vars_decision = m * n
        num_vars_holgura = m
        
        if columna < num_vars_decision:
            # Variable de decisión xij
            i = columna // n
            j = columna % n
            return f"x{i+1}{j+1}"
        elif columna < num_vars_decision + num_vars_holgura:
            # Variable de holgura
            i = columna - num_vars_decision
            return f"s{i+1}"
        else:
            # Variable artificial
            j = columna - num_vars_decision - num_vars_holgura
            return f"a{j+1}"
    
    def _registrar_iteracion(self, es_final: bool = False) -> None:
        """
        Registra el estado actual de la tabla como una iteración
        
        Args:
            es_final: Si es la iteración final
        """
        # Convertir tabla a formato JSON serializable
        tabla_json = []
        for fila in self.tabla:
            fila_json = [float(elemento) for elemento in fila]
            tabla_json.append(fila_json)
        
        iteracion = {
            "iteration": self.num_iteracion,
            "tableau": tabla_json,
            "basic_vars": self.variables_basicas[:],
            "is_optimal": es_final or self._es_optimo()
        }
        
        # Agregar información de variables entrante y saliente si no es final
        if not es_final and not self._es_optimo():
            columna_entrante = self._seleccionar_variable_entrante()
            if columna_entrante != -1:
                iteracion["entering_var"] = self._obtener_nombre_variable(columna_entrante)
                
                fila_saliente = self._prueba_razon_minima(columna_entrante)
                if fila_saliente != -1:
                    iteracion["leaving_var"] = self.variables_basicas[fila_saliente]
                    iteracion["pivot_element"] = float(self.tabla[fila_saliente][columna_entrante])
        
        self.iteraciones.append(iteracion)
    
    def _hay_variables_artificiales_en_base(self) -> bool:
        """
        Verifica si hay variables artificiales con valor positivo en la solución
        
        Returns:
            bool: True si el problema es infactible
        """
        for i, var in enumerate(self.variables_basicas):
            if var in self.variables_artificiales and self.tabla[i][-1] > Fraction(1, 1000000):
                return True
        return False
    
    def _construir_solucion_final(self, m: int, n: int, tipo_optimizacion: str) -> Dict[str, Any]:
        """
        Construye la respuesta final del problema
        
        Args:
            m: Número de orígenes
            n: Número de destinos
            tipo_optimizacion: Tipo de optimización original
            
        Returns:
            Dict con la solución completa
        """
        # Extraer valores de variables de decisión
        solucion_matriz = [[0.0 for _ in range(n)] for _ in range(m)]
        variables_basicas_finales = []
        
        for i, var in enumerate(self.variables_basicas):
            if var.startswith('x'):
                # Extraer índices i, j de la variable xij
                indices = var[1:]  # Remover 'x'
                idx_i = int(indices[0]) - 1
                idx_j = int(indices[1]) - 1
                
                if 0 <= idx_i < m and 0 <= idx_j < n:
                    valor = float(self.tabla[i][-1])
                    if valor > 1e-10:  # Solo valores significativos
                        solucion_matriz[idx_i][idx_j] = valor
                        variables_basicas_finales.append(var)
        
        # Calcular valor óptimo
        valor_optimo = float(self.tabla[-1][-1])
        if tipo_optimizacion == "maximize":
            valor_optimo = -valor_optimo
        
        # Generar interpretación
        interpretacion = self._generar_interpretacion(solucion_matriz, m, n, valor_optimo)
        
        return {
            "status": "optimal",
            "method_used": "gran_m",
            "optimal_value": valor_optimo,
            "solution_matrix": solucion_matriz,
            "basic_variables": variables_basicas_finales,
            "iterations": self.iteraciones,
            "interpretation": interpretacion,
            "total_iterations": self.num_iteracion,
            "execution_time": 0  # Se medirá externamente
        }
    
    def _generar_interpretacion(self, solucion: List[List[float]], 
                              m: int, n: int, valor_optimo: float) -> str:
        """
        Genera una interpretación en lenguaje natural de la solución
        
        Args:
            solucion: Matriz de solución
            m: Número de orígenes
            n: Número de destinos
            valor_optimo: Valor óptimo de la función objetivo
            
        Returns:
            str: Interpretación textual de la solución
        """
        interpretacion = f"SOLUCIÓN ÓPTIMA DEL PROBLEMA DE TRANSPORTE\n\n"
        interpretacion += f"Costo mínimo total: {valor_optimo:.2f} unidades monetarias\n\n"
        interpretacion += "Plan de transporte óptimo:\n"
        
        for i in range(m):
            for j in range(n):
                cantidad = solucion[i][j]
                if cantidad > 1e-6:  # Solo mostrar cantidades significativas
                    interpretacion += f"• Transportar {cantidad:.2f} unidades desde Origen {i+1} hacia Destino {j+1}\n"
        
        # Calcular totales por origen y destino
        interpretacion += "\nResumen por orígenes:\n"
        for i in range(m):
            total_enviado = sum(solucion[i])
            if total_enviado > 1e-6:
                interpretacion += f"• Origen {i+1}: {total_enviado:.2f} unidades enviadas\n"
        
        interpretacion += "\nResumen por destinos:\n"
        for j in range(n):
            total_recibido = sum(solucion[i][j] for i in range(m))
            if total_recibido > 1e-6:
                interpretacion += f"• Destino {j+1}: {total_recibido:.2f} unidades recibidas\n"
        
        return interpretacion
    
    def _resultado_infactible(self) -> Dict[str, Any]:
        """
        Genera resultado para problema infactible
        """
        return {
            "status": "infeasible",
            "method_used": "gran_m",
            "message": "El problema es infactible - no existe solución que satisfaga todas las restricciones",
            "iterations": self.iteraciones,
            "total_iterations": self.num_iteracion
        }
    
    def _resultado_no_acotado(self) -> Dict[str, Any]:
        """
        Genera resultado para problema no acotado
        """
        return {
            "status": "unbounded",
            "method_used": "gran_m",
            "message": "El problema es no acotado - la función objetivo puede decrecer indefinidamente",
            "iterations": self.iteraciones,
            "total_iterations": self.num_iteracion
        }


def main():
    """
    Función principal para ejecutar el solver desde línea de comandos
    Lee datos JSON desde stdin y retorna resultado en stdout
    """
    try:
        # Leer datos desde stdin
        entrada = sys.stdin.read()
        datos = json.loads(entrada)
        
        # Extraer parámetros
        costos = datos['cost_matrix']
        ofertas = datos['supply']
        demandas = datos['demand']
        tipo_opt = datos.get('optimization_type', 'minimize')
        
        # Resolver problema
        solver = GranMSolver()
        resultado = solver.resolver_gran_m(costos, ofertas, demandas, tipo_opt)
        
        # Retornar resultado
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        
    except Exception as e:
        # Manejo de errores
        resultado_error = {
            "status": "error",
            "message": f"Error en solver Gran M: {str(e)}",
            "iterations": []
        }
        print(json.dumps(resultado_error, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### A.4 Configuración del Proyecto

#### A.4.1 package.json
```json
{
  "name": "transport-optimization-system",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "description": "Sistema de optimización de transporte usando métodos Simplex",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "start:backend": "python -m uvicorn python_wrapper:app --reload --port 8000",
    "start:fullstack": "concurrently \"npm run start:backend\" \"npm run dev\""
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.15",
    "@types/react-dom": "^18.2.7",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.0.3",
    "autoprefixer": "^10.4.14",
    "concurrently": "^8.2.0",
    "eslint": "^8.45.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.3",
    "postcss": "^8.4.27",
    "tailwindcss": "^3.3.3",
    "typescript": "^5.0.2",
    "vite": "^4.4.5"
  }
}
```

## Anexo B: Manual del Usuario

### B.1 Requisitos del Sistema

#### B.1.1 Requisitos de Hardware
- **Procesador**: Intel i3 o equivalente AMD (mínimo)
- **Memoria RAM**: 4 GB (recomendado 8 GB)
- **Espacio en disco**: 500 MB libres
- **Resolución de pantalla**: 1280x720 píxeles (mínimo)

#### B.1.2 Requisitos de Software
- **Sistema Operativo**: Windows 10/11, macOS 10.15+, o Linux Ubuntu 18.04+
- **Navegador Web**: Chrome 90+, Firefox 88+, Safari 14+, o Edge 90+
- **Node.js**: Versión 16.0 o superior
- **Python**: Versión 3.8 o superior
- **npm**: Versión 7.0 o superior (incluido con Node.js)

### B.2 Instalación del Sistema

#### B.2.1 Instalación de Dependencias

1. **Instalar Node.js**
   - Descargar desde: https://nodejs.org/
   - Seguir el instalador para su sistema operativo
   - Verificar instalación: `node --version` y `npm --version`

2. **Instalar Python**
   - Descargar desde: https://python.org/
   - Asegurar que se agregue al PATH del sistema
   - Verificar instalación: `python --version`

3. **Instalar dependencias de Python**
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

#### B.2.2 Configuración del Proyecto

1. **Descargar el proyecto**
   - Descomprimir el archivo del proyecto en una carpeta de su elección
   - Ejemplo: `C:\TransportOptimization\` (Windows) o `~/TransportOptimization/` (macOS/Linux)

2. **Instalar dependencias del frontend**
   ```bash
   cd TransportOptimization
   npm install
   ```

3. **Verificar estructura de archivos**
   ```
   TransportOptimization/
   ├── src/
   ├── public/
   ├── package.json
   ├── python_wrapper.py
   └── README.md
   ```

### B.3 Ejecución del Sistema

#### B.3.1 Inicio del Sistema Completo

**Opción 1: Inicio automático (Recomendado)**
```bash
npm run start:fullstack
```
Este comando inicia automáticamente tanto el backend como el frontend.

**Opción 2: Inicio manual**
1. **Terminal 1 - Backend:**
   ```bash
   npm run start:backend
   ```
   
2. **Terminal 2 - Frontend:**
   ```bash
   npm run dev
   ```

#### B.3.2 Verificación de Funcionamiento

1. **Verificar backend**: Abrir http://localhost:8000/docs
   - Debería mostrar la documentación automática de la API

2. **Verificar frontend**: Abrir http://localhost:5173
   - Debería mostrar la interfaz del sistema de optimización

### B.4 Uso del Sistema

#### B.4.1 Configuración del Problema

1. **Acceder al sistema**
   - Abrir navegador web
   - Navegar a http://localhost:5173
   - Esperar a que cargue completamente la interfaz

2. **Configurar dimensiones del problema**
   - **Número de Orígenes**: Seleccionar entre 1 y 10
   - **Número de Destinos**: Seleccionar entre 1 y 10
   - **Método de Solución**: Elegir "Gran M" o "Dos Fases"
   - **Tipo de Optimización**: Seleccionar "Minimizar" o "Maximizar"

3. **Ejemplo de configuración básica**
   - Orígenes: 3 (tres granjas)
   - Destinos: 3 (tres mercados)
   - Método: Gran M
   - Optimización: Minimizar costos

#### B.4.2 Entrada de Datos

1. **Matriz de Costos**
   - Llenar cada celda con el costo de transportar una unidad
   - Los valores deben ser números positivos
   - Ejemplo para 2×2:
     ```
     [2] [3]
     [4] [1]
     ```

2. **Capacidades de Oferta**
   - Ingresar la capacidad de cada origen
   - Valores deben ser números positivos
   - Ejemplo: [20, 30, 25]

3. **Demandas de Destinos**
   - Ingresar la demanda de cada destino
   - Valores deben ser números positivos
   - Ejemplo: [15, 25, 35]

#### B.4.3 Validación de Datos

El sistema valida automáticamente:
- **Dimensiones**: Coherencia entre matriz y vectores
- **Valores numéricos**: Solo números positivos
- **Formato**: Detección de campos vacíos o inválidos

**Mensajes de error comunes:**
- "Los costos deben ser números positivos"
- "La matriz de costos debe estar completa"
- "Las ofertas deben ser mayores que cero"

#### B.4.4 Resolución del Problema

1. **Ejecutar solución**
   - Hacer clic en el botón "Resolver Problema"
   - Esperar mientras se procesa (indicador de carga)
   - El tiempo de procesamiento depende del tamaño del problema

2. **Interpretación de resultados**
   - **Estado**: Óptimo, Infactible, No acotado, o Error
   - **Valor óptimo**: Costo mínimo (o máximo beneficio)
   - **Plan de transporte**: Cantidades específicas a transportar
   - **Iteraciones**: Proceso paso a paso del algoritmo

#### B.4.5 Visualización de Resultados

1. **Tabla de Solución Final**
   - Matriz que muestra las cantidades óptimas de transporte
   - Filas: Orígenes, Columnas: Destinos
   - Valores: Unidades a transportar

2. **Interpretación Contextual**
   - Descripción en lenguaje natural
   - Plan específico de transporte
   - Resumen por orígenes y destinos

3. **Historial de Iteraciones**
   - Tabla simplex de cada iteración
   - Variables que entran y salen de la base
   - Elementos pivote utilizados

### B.5 Casos de Uso Típicos

#### B.5.1 Problema de Transporte Básico

**Escenario**: Una empresa tiene 2 almacenes y debe abastecer 3 tiendas.

**Datos de entrada**:
- Almacenes: 2
- Tiendas: 3
- Costos de transporte:
  ```
  Almacén 1 → Tienda 1: $8/unidad
  Almacén 1 → Tienda 2: $6/unidad
  Almacén 1 → Tienda 3: $10/unidad
  Almacén 2 → Tienda 1: $9/unidad
  Almacén 2 → Tienda 2: $12/unidad
  Almacén 2 → Tienda 3: $13/unidad
  ```
- Capacidades: [50, 70] unidades
- Demandas: [30, 40, 50] unidades

**Pasos**:
1. Configurar: 2 orígenes, 3 destinos, método Gran M, minimizar
2. Ingresar matriz de costos: [[8,6,10],[9,12,13]]
3. Ingresar ofertas: [50, 70]
4. Ingresar demandas: [30, 40, 50]
5. Resolver problema
6. Interpretar resultados

#### B.5.2 Problema de Maximización

**Escenario**: Maximizar beneficios de distribución de productos.

**Diferencias**:
- Seleccionar "Maximizar" en tipo de optimización
- Los valores en la matriz representan beneficios por unidad
- El resultado será el beneficio máximo posible

#### B.5.3 Problema No Balanceado

**Escenario**: La oferta total no es igual a la demanda total.

**Comportamiento del sistema**:
- El sistema automáticamente balancea el problema
- Agrega origen o destino ficticio según sea necesario
- La solución incluye variables de holgura cuando sea relevante

### B.6 Solución de Problemas

#### B.6.1 Problemas de Instalación

**Error: "npm no reconocido"**
- Solución: Reinstalar Node.js y verificar que esté en el PATH

**Error: "python no reconocido"**
- Solución: Reinstalar Python y marcar "Add to PATH" durante instalación

**Error: "Puerto 8000 en uso"**
- Solución: Cerrar otras aplicaciones que usen el puerto o cambiar puerto en código

#### B.6.2 Problemas de Ejecución

**Error: "No se puede conectar con el servidor"**
- Verificar que el backend esté ejecutándose (http://localhost:8000/docs)
- Reiniciar el backend: `npm run start:backend`

**Error: "Timeout de operación"**
- Reducir el tamaño del problema (menos orígenes/destinos)
- Verificar que los datos sean válidos

**Error: "Problema infactible"**
- Verificar que la suma de ofertas sea igual o mayor a la suma de demandas
- Revisar que todos los valores sean positivos

#### B.6.3 Problemas de Interfaz

**La página no carga correctamente**
- Limpiar caché del navegador (Ctrl+F5)
- Probar en modo incógnito
- Verificar que no haya bloqueadores de JavaScript

**Los resultados no se muestran**
- Verificar la consola del navegador (F12)
- Comprobar conexión con el backend
- Revisar que los datos de entrada sean válidos

### B.7 Limitaciones y Consideraciones

#### B.7.1 Limitaciones Técnicas

- **Tamaño máximo**: 10×10 (100 variables de decisión)
- **Precisión numérica**: 10 decimales
- **Tiempo máximo**: 30 segundos por problema
- **Memoria**: Optimizado para problemas de tamaño medio

#### B.7.2 Consideraciones de Rendimiento

- Problemas 5×5 o menores: < 2 segundos
- Problemas 10×10: < 5 segundos
- Usar "Gran M" para problemas simples
- Usar "Dos Fases" para mejor estabilidad numérica

#### B.7.3 Mejores Prácticas

1. **Preparación de datos**
   - Verificar datos antes de ingresarlos
   - Usar números enteros cuando sea posible
   - Evitar valores muy grandes (>1000)

2. **Interpretación de resultados**
   - Verificar que la solución tenga sentido práctico
   - Comparar resultados entre métodos Gran M y Dos Fases
   - Revisar el historial de iteraciones para entender el proceso

3. **Depuración de problemas**
   - Empezar con problemas pequeños (2×2)
   - Incrementar gradualmente el tamaño
   - Documentar casos que no funcionan correctamente

### B.8 Soporte y Contacto

Para problemas técnicos o preguntas sobre el uso del sistema:

1. **Documentación**: Revisar este manual completo
2. **Logs del sistema**: Verificar la consola del navegador (F12)
3. **Archivos de configuración**: Verificar package.json y configuración

**Información del sistema**:
- Versión: 1.0
- Última actualización: 2025
- Compatibilidad: Navegadores modernos
- Soporte: Documentación incluida
