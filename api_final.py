#!/usr/bin/env python3
"""
API Final Completa - Soporta tanto Dos Fases como Gran M
Puerto: 8003
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import uvicorn
import sys
import os

# Agregar path para importar métodos existentes
components_path = os.path.join(os.path.dirname(__file__), 'src', 'components')
if components_path not in sys.path:
    sys.path.insert(0, components_path)

# Import del método Gran M
try:
    from MetodoM_NEW import SimplexTablaInicialCompleta
    GRANM_AVAILABLE = True
    print("✅ Método Gran M importado exitosamente")
except ImportError as e:
    GRANM_AVAILABLE = False
    print(f"⚠️ No se pudo importar método Gran M: {e}")

# Import del método Dos Fases COMPLETO
try:
    from src.components.Metodo2F_NEW import SimplexDosFasesTablaCompleta
    DOSFASES_AVAILABLE = True
    print("✅ Método Dos Fases COMPLETO importado exitosamente")
except ImportError as e:
    DOSFASES_AVAILABLE = False
    print(f"⚠️ No se pudo importar método Dos Fases completo: {e}")
    
    # Fallback al método anterior
    try:
        from Metodo2F_NEW import SimplexDosFasesTablaCompleta
        DOSFASES_AVAILABLE = True
        print("✅ Método Dos Fases básico importado como fallback")
    except ImportError as e2:
        print(f"⚠️ No se pudo importar método Dos Fases: {e2}")

app = FastAPI(title="Transport Solver - API Final Completa", version="Final v2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SolverRequest(BaseModel):
    n_vars: int
    n_cons: int
    c: List[float]
    A: List[List[float]]
    b: List[float]
    signs: List[str]
    obj_type: Literal["max", "min"]
    method: Literal["granm", "dosfases"]

@app.get("/")
async def root():
    return {
        "message": "API Final Completa - Método Simplex con Iteraciones Detalladas", 
        "version": "Final v2.0",
        "methods_available": {
            "dosfases": DOSFASES_AVAILABLE,
            "granm": GRANM_AVAILABLE
        }
    }

@app.post("/solve")
async def solve_problem(data: SolverRequest):
    """API que soporta tanto Dos Fases como Gran M con iteraciones completas"""
    try:
        print(f"🔍 API Final: Resolviendo {data.method} - {data.obj_type}")
        print(f"📊 Problema: {data.n_vars} vars, {data.n_cons} restricciones")
        
        if data.method == "dosfases":
            if not DOSFASES_AVAILABLE:
                return {"error": "Método Dos Fases no disponible"}
                
            # Usar implementación completa
            solver = SimplexDosFasesTablaCompleta()
            result = solver.solve_from_data(
                n_vars=data.n_vars,
                n_cons=data.n_cons,
                c=data.c,
                A=data.A,
                b=data.b,
                signs=data.signs,
                obj_type=data.obj_type
            )
            print("✅ API Final: Dos Fases ejecutado exitosamente")
            print(f"📈 Resultado: {result.get('fase2', {}).get('optimo', 'N/A') if 'fase2' in result else 'Solo Fase 1'}")
            return result
        
        elif data.method == "granm":
            if not GRANM_AVAILABLE:
                return {"error": "Método Gran M no disponible"}
                
            # Usar método Gran M existente
            solver = SimplexTablaInicialCompleta()
            result = solver.solve_from_data(
                n_vars=data.n_vars,
                n_cons=data.n_cons,
                c=data.c,
                A=data.A,
                b=data.b,
                signs=data.signs,
                obj_type=data.obj_type
            )
            print("✅ API Final: Gran M ejecutado exitosamente")
            return result
            
        else:
            return {"error": f"Método {data.method} no soportado"}
            
    except Exception as e:
        print(f"❌ API Final: Error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Error interno: {str(e)}"}

@app.get("/test/{method}")
async def test_method(method: Literal["dosfases", "granm"]):
    """Endpoint de prueba para verificar que los métodos funcionan"""
    test_data = {
        "n_vars": 2,
        "n_cons": 2,
        "c": [2, 1],
        "A": [[1, 1], [2, 1]],
        "b": [3, 4],
        "signs": ["<=", "<="],
        "obj_type": "min",
        "method": method
    }
    
    request = SolverRequest(**test_data)
    return await solve_problem(request)

if __name__ == "__main__":
    print("🚀 Iniciando API Final Completa - Puerto 8003")
    print("🔧 Implementación completa del método Simplex con iteraciones detalladas")
    
    if DOSFASES_AVAILABLE:
        print("✅ Método Dos Fases COMPLETO disponible")
    else:
        print("⚠️ Método Dos Fases no disponible")
        
    if GRANM_AVAILABLE:
        print("✅ Método Gran M disponible")
    else:
        print("⚠️ Método Gran M no disponible")
        
    print("\n🌐 Endpoints disponibles:")
    print("  GET  /           - Info del API")
    print("  POST /solve      - Resolver problema")
    print("  GET  /test/{method} - Probar método")
    
    uvicorn.run("api_final:app", host="0.0.0.0", port=8003, reload=False)