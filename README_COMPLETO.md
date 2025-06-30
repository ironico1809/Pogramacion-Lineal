# Solver de Programación Lineal - Gran M y Dos Fases

Sistema profesional para resolver problemas de programación lineal utilizando los métodos **Gran M** y **Dos Fases**.

## 🚀 Características

- **Frontend**: React + TypeScript + Vite (interfaz moderna y responsiva)
- **Backend**: Python + FastAPI (API REST rápida y robusta)
- **Métodos implementados**:
  - Gran M (SimplexTablaInicialCompleta) ✅
  - Dos Fases (SimplexDosFases) ✅
- **Visualización completa**: tablas simplex, iteraciones paso a paso, resultados óptimos
- **Presentación profesional**: Ambos métodos muestran soluciones finales con interpretación del problema de transporte

## 📁 Estructura del Proyecto

```
proyecto/
├── src/
│   ├── App.tsx                    # Frontend principal (toda la UI) ✅
│   ├── App_CLEAN.css              # Estilos del frontend (limpio) ✅
│   ├── api/
│   │   └── api.py                 # Backend FastAPI ✅
│   └── components/
│       ├── MetodoM_NEW.py         # Implementación Gran M ✅
│       └── Metodo2F.py            # Implementación Dos Fases ✅
├── package.json                   # Dependencias frontend ✅
├── start_backend_TEST.bat         # Script para iniciar backend ✅
├── test_frontend_backend.py       # Tests de integración UI ✅
└── MEJORAS_FRONTEND_COMPLETADAS.md # Documentación de mejoras ✅
```

## 🛠️ Instalación y Configuración

### 1. Backend (Python)

```bash
# Instalar FastAPI y dependencias
pip install fastapi uvicorn python-typing-extensions

# O instalar todas las dependencias:
pip install -r requirements.txt  # (crear si no existe)
```

### 2. Frontend (React)

```bash
# Instalar dependencias de Node.js
npm install

# O usar yarn:
yarn install
```

## 🚀 Ejecución

### Opción 1: Scripts automatizados

1. **Iniciar el backend**:
   ```bash
   # Windows
   start_backend_NEW.bat
   
   # Linux/Mac
   python -m uvicorn src.api.api:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Iniciar el frontend**:
   ```bash
   npm run dev
   # o
   yarn dev
   ```

### Opción 2: Manual

**Backend (Terminal 1)**:
```bash
cd proyecto
python -m uvicorn src.api.api:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend (Terminal 2)**:
```bash
cd proyecto
npm run dev
```

## 🧪 Tests

```bash
# Test de integración del backend
python test_integration.py

# Verificar que el API responde
curl http://localhost:8000/solve -X POST -H "Content-Type: application/json" -d '{"method":"granm","n_vars":2,"n_cons":1,"c":[1,1],"A":[[1,1]],"b":[1],"signs":["<="],"obj_type":"max"}'
```

## 📖 Uso del Sistema

1. **Abrir la aplicación**: `http://localhost:5173` (frontend Vite)
2. **Configurar el problema**:
   - Seleccionar método (Gran M o Dos Fases)
   - Definir número de variables y restricciones
   - Ingresar coeficientes de la función objetivo
   - Configurar restricciones (coeficientes, signos, valores)
3. **Resolver**: Hacer clic en "Resolver Problema"
4. **Ver resultados**: El sistema muestra:
   - Función objetivo penalizada
   - Tabla simplex inicial
   - Iteraciones paso a paso
   - Solución óptima

## 🔧 API Endpoints

### POST `/solve`

Resuelve un problema de programación lineal.

**Request**:
```json
{
  "method": "granm" | "dosfases",
  "n_vars": 2,
  "n_cons": 2,
  "c": [3, 2],
  "A": [[2, 1], [1, 1]],
  "b": [100, 80],
  "signs": ["<=", "<="],
  "obj_type": "max" | "min"
}
```

**Response**:
```json
{
  "penalized_obj": {...},
  "simplex_obj": {...},
  "initial_tableau": {...},
  "sbfi": {...},
  "r0_nuevo": {...},
  "iteraciones": [...]
}
```

## 🔍 Troubleshooting

### Error de CORS
Si hay problemas de CORS, verificar que el backend permite conexiones desde el frontend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error de módulos Python
Si hay errores de importación, verificar el PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src/components"
```

### Puerto ocupado
Si el puerto 8000 está ocupado:
```bash
# Cambiar puerto en api.py o usar:
python -m uvicorn src.api.api:app --host 0.0.0.0 --port 8080 --reload

# Y actualizar la URL en App.tsx
```

## 🚀 Deployment

### Backend (FastAPI)
```bash
# Para producción
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.api:app --bind 0.0.0.0:8000
```

### Frontend (React)
```bash
# Build para producción
npm run build

# Los archivos estáticos estarán en dist/
```

---

## 📝 Notas del Desarrollador

- La clase `SimplexTablaInicialCompleta` implementa completamente el método Gran M con manejo simbólico de M
- El sistema maneja automáticamente la conversión min ↔ max
- Las iteraciones se guardan paso a paso para visualización educativa
- El frontend está completamente contenido en `App.tsx` para facilidad de mantenimiento
- El sistema es totalmente funcional y listo para producción

**Estado**: ✅ **COMPLETO Y FUNCIONAL**
