# 🚀 GUÍA COMPLETA - API CON AMBOS MÉTODOS

## ✅ Solución Implementada

La API ahora soporta **AMBOS métodos**:
- ✅ **Método Dos Fases** (`"method": "dosfases"`)
- ✅ **Método Gran M** (`"method": "granm"`)

## 🔧 Para Iniciar y Probar

### 1. Iniciar el Servidor API
```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Iniciar servidor (puerto 8003)
python api_final.py
```

### 2. Probar Ambos Métodos
En otra terminal:
```bash
# Test completo de ambos métodos
python test_api_dos_fases.py
```

### 3. Iniciar Frontend React
```bash
# En otra terminal
npm run dev
```

## 📡 Endpoints de la API

### URL Base
```
http://localhost:8003
```

### POST /solve
Acepta ambos métodos:

#### Método Dos Fases
```json
{
  "n_vars": 2,
  "n_cons": 2,
  "c": [2000, 500],
  "A": [[2, 3], [3, 6]],
  "b": [36, 60],
  "signs": [">=", ">="],
  "obj_type": "min",
  "method": "dosfases"
}
```

#### Método Gran M  
```json
{
  "n_vars": 2,
  "n_cons": 2,
  "c": [2000, 500],
  "A": [[2, 3], [3, 6]],
  "b": [36, 60],
  "signs": [">=", ">="],
  "obj_type": "min",
  "method": "granm"
}
```

## 🧪 Tests Disponibles

- `test_api_dos_fases.py` - Test completo de ambos métodos
- `test_direct_methods.py` - Test directo sin servidor
- `test_integral_final.py` - Test exhaustivo del método Dos Fases
- `test_both_methods.py` - Test específico para comparar métodos

## ✅ Características

1. **Ambos métodos funcionan** - Gran M y Dos Fases
2. **Puerto único** - 8003 para toda la API
3. **Frontend compatible** - Ya configurado para puerto 8003
4. **Respuesta consistente** - Formato unificado para ambos métodos
5. **Sin errores hardcodeados** - Eliminado completamente

## 🎯 Resultado Esperado

Ambos métodos deben devolver:
```json
{
  "optimal_solution": {"x1": valor, "x2": valor},
  "optimal_value": numero,
  "status": "optimal",
  "iteraciones": [...]
}
```

## 🚨 Troubleshooting

### Si el servidor no inicia:
1. Verificar que el entorno virtual esté activado
2. Instalar dependencias: `pip install -r requirements.txt`
3. Verificar puerto 8003 disponible

### Si hay errores de importación:
1. Los métodos se importan automáticamente
2. Gran M desde `src/components/MetodoM_NEW.py`
3. Dos Fases embedded en `api_final.py`

### Si el frontend no conecta:
1. Verificar URL: `http://localhost:8003/solve`
2. Frontend debe estar en puerto 5173
3. CORS habilitado automáticamente

## 🎉 Estado: COMPLETAMENTE FUNCIONAL

- ✅ **Gran M**: Funciona correctamente
- ✅ **Dos Fases**: Sin error hardcodeado, completamente generalizado
- ✅ **API unificada**: Un solo servidor para ambos métodos
- ✅ **Frontend**: Compatible con ambos métodos
