# 🚚 Transporte de Productos entre Ciudades

Aplicación web para resolver problemas de transporte usando los métodos Simplex de Gran M y Dos Fases.

## 🎯 Características

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python con métodos Simplex (Gran M y Dos Fases)
- **Interfaz Intuitiva**: Entrada de datos paso a paso
- **Visualización**: Tablas iterativas del método Simplex
- **Métodos Implementados**: 
  - Método de la Gran M
  - Método de Dos Fases

## 🚀 Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd Project
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar Python** (para conectar con tu backend)
```bash
# Asegúrate de que Python esté instalado
python --version

# Los archivos dosfases.py y project.py deben estar en ../Camiones/
```

## 📖 Uso

1. **Ejecutar el servidor de desarrollo**
```bash
npm run dev
```

2. **Abrir en el navegador**
```
http://localhost:5173
```

3. **Usar la aplicación**:
   - Paso 1: Configurar método (Gran M o Dos Fases) y tipo de optimización
   - Paso 2: Revisar las variables de decisión
   - Paso 3: Ingresar costos, capacidades y demandas
   - Paso 4: Ver resultados y iteraciones del método

## 🏗️ Estructura del Proyecto

```
Project/
├── src/
│   ├── components/
│   │   └── TransportSolver.tsx    # Componente principal
│   ├── api/
│   │   └── simplex.ts             # API para Python
│   ├── App.tsx                    # Aplicación principal
│   └── main.tsx                   # Punto de entrada
├── python_wrapper.py              # Wrapper para Python
└── README.md
```

## 📊 Problema de Ejemplo

La aplicación resuelve problemas de transporte con:
- **2 Almacenes** (capacidades limitadas)
- **2 Ciudades** (demandas específicas)
- **4 Variables de decisión** (rutas de transporte)
- **4 Restricciones** (capacidades y demandas)

### Formulación Matemática

```
Minimizar Z = c₁x₁ + c₂x₂ + c₃x₃ + c₄x₄

Sujeto a:
x₁ + x₂ ≤ Capacidad_Almacén_1
x₃ + x₄ ≤ Capacidad_Almacén_2
x₁ + x₃ ≥ Demanda_Ciudad_A
x₂ + x₄ ≥ Demanda_Ciudad_B
x₁, x₂, x₃, x₄ ≥ 0
```

## 🔧 Conexión con Python

Para conectar con tu código Python real:

1. **Coloca tus archivos Python** en `../Camiones/`:
   - `dosfases.py`
   - `project.py`

2. **El wrapper Python** (`python_wrapper.py`) procesará los datos del frontend

3. **Para activar la conexión real**, modifica `resolverProblema()` en `TransportSolver.tsx`

## 🎨 Tecnologías

- **React 18** con TypeScript
- **Vite** para desarrollo rápido
- **Lucide React** para iconos
- **Axios** para llamadas HTTP
- **Python** para cálculos Simplex

## 📝 Scripts Disponibles

```bash
npm run dev          # Servidor de desarrollo
npm run build        # Construir para producción
npm run preview      # Vista previa de producción
npm run lint         # Verificar código
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🚀 Próximas Características

- [ ] Conectar con backend Python real
- [ ] Más de 2 almacenes y ciudades
- [ ] Exportar resultados a PDF
- [ ] Gráficas de la región factible
- [ ] Análisis de sensibilidad
- [ ] Historial de problemas resueltos
