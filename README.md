# Optimizador de Transporte - Métodos Simplex

Sistema de optimización de problemas de transporte utilizando los métodos Simplex de **Gran M** y **Dos Fases**. 

## 🎯 Características

- **Frontend**: React + TypeScript + Vite con interfaz interactiva
- **Backend**: Python con FastAPI para resolver problemas de optimización
- **Métodos**: Gran M y Dos Fases con visualización paso a paso
- **Casos de uso**: Problemas de transporte, asignación de recursos, minimización de costos

## 🚀 Instalación y Uso

### Requisitos
- Node.js (v16 o superior)
- Python 3.8+
- pip (gestor de paquetes Python)

### Instalación

1. **Clonar el repositorio**:
```bash
git clone [URL_DEL_REPOSITORIO]
cd Project
```

2. **Instalar dependencias del frontend**:
```bash
npm install
```

3. **Instalar dependencias del backend**:
```bash
pip install fastapi uvicorn python-multipart
```

### Ejecutar la aplicación

1. **Iniciar el backend**:
```bash
# Opción 1: Script automático (Windows)
start_backend.bat

# Opción 2: Manual
cd src/api
python api.py
```

2. **Iniciar el frontend**:
```bash
npm run dev
```

3. **Acceder a la aplicación**:
   - Frontend: http://localhost:5173
   - API Backend: http://localhost:8000

## 📋 Limitaciones del Sistema

**IMPORTANTE**: El programa tiene las siguientes limitaciones técnicas:

### 🔢 Limitaciones de Tamaño
- **Máximo 10 variables de decisión**
- **Máximo 10 restricciones**
- *Razón*: Rendimiento de la interfaz web y visualización clara

### 📝 Limitaciones de Formato de Entrada
- **Solo números decimales** con punto (.) como separador decimal
- **No acepta fracciones** como entrada (ej: 1/2, 3/4)
- **No acepta comas** como separador decimal
- *Ejemplo válido*: 12.5, 0.33, -5.75
- *Ejemplo inválido*: 12,5 o 1/2

### 🧮 Limitaciones de Tipo de Problema
- **Solo programación lineal continua**
- **No programación entera** (variables enteras)
- **No programación no lineal** (funciones no lineales)
- **No programación binaria** (variables 0-1)

### ⚠️ Limitaciones de Coeficientes
- **Solo números finitos** (no infinitos ni NaN)
- **Coeficientes válidos**: cualquier número decimal finito
- **Coeficientes inválidos**: ∞, -∞, NaN, undefined

### 📊 Tipos de Restricción Soportados
- **≤** (menor o igual)
- **≥** (mayor o igual)  
- **=** (igual)

## 🎓 Uso Académico

Este proyecto está diseñado para:
- **Enseñanza** de métodos Simplex
- **Demostración** paso a paso de algoritmos
- **Investigación** en optimización lineal
- **Prototipado** de sistemas de optimización

Para documentación académica completa, consultar:
- `DOCUMENTACION_ACADEMICA.md`: Metodología y resultados
- `METODOLOGIA.md`: Detalles algorítmicos

## 🛠️ Tecnologías Utilizadas

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React (iconos)

### Backend  
- Python 3.8+
- FastAPI
- Uvicorn
- Métodos Simplex personalizados

## 📄 Documentación Adicional

- **Tutorial integrado** en la aplicación web
- **Ejemplos predefinidos** para casos de transporte
- **Visualización de iteraciones** paso a paso
- **Interpretación contextual** de resultados
