# 🚚 Ejemplo de Uso - Transporte de Productos

## Datos de Prueba Sugeridos

Para probar la aplicación, puedes usar los siguientes datos:

### 📊 Configuración
- **Método**: Gran M o Dos Fases
- **Optimización**: Minimizar Costos

### 💰 Costos de Transporte ($/unidad)
- Almacén 1 → Ciudad A: **3**
- Almacén 1 → Ciudad B: **5**
- Almacén 2 → Ciudad A: **4**
- Almacén 2 → Ciudad B: **2**

### 🏢 Capacidades de Almacenes
- Almacén 1: **100** unidades
- Almacén 2: **80** unidades

### 🏙️ Demandas de Ciudades
- Ciudad A: **60** unidades
- Ciudad B: **70** unidades

## 📋 Problema Resultante

**Minimizar Z = 3x₁ + 5x₂ + 4x₃ + 2x₄**

**Sujeto a:**
- x₁ + x₂ ≤ 100 (Capacidad Almacén 1)
- x₃ + x₄ ≤ 80 (Capacidad Almacén 2)
- x₁ + x₃ ≥ 60 (Demanda Ciudad A)
- x₂ + x₄ ≥ 70 (Demanda Ciudad B)
- x₁, x₂, x₃, x₄ ≥ 0

## 🎯 Resultado Esperado

Con estos datos, la aplicación debería encontrar una solución que:
1. Satisfaga todas las demandas
2. Respete las capacidades
3. Minimice el costo total de transporte

## 🚀 Ejecutar el Ejemplo

1. Abre http://localhost:5174/ en tu navegador
2. Selecciona "Método de la Gran M" y "Minimizar Costos"
3. Continúa a las variables (ya están definidas)
4. Ingresa los datos de costos, capacidades y demandas mostrados arriba
5. Haz clic en "Resolver Problema"
6. Revisa las iteraciones y la solución óptima

## 🔄 Otros Ejemplos

### Ejemplo 2: Maximizar Beneficios
- Cambia a "Maximizar Beneficios"
- Usa los mismos datos pero interprétalos como beneficios por unidad
- Compara las diferencias en la solución

### Ejemplo 3: Método Dos Fases
- Usa el "Método de Dos Fases"
- Mismos datos del Ejemplo 1
- Observa las diferencias en las iteraciones
