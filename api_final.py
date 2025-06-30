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

from dos_fases_corregido import solve_dos_fases_corregido

app = FastAPI(title="Transport Solver - API Final", version="Final")

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
    return {"message": "API Final - Método Dos Fases Funcional", "version": "Final"}

@app.post("/solve")
async def solve_problem(data: SolverRequest):
    """API que soporta tanto Dos Fases como Gran M"""
    try:
        print(f"🔍 API Final: Resolviendo {data.method} - {data.obj_type}")
        
        if data.method == "dosfases":
            # Usar la nueva implementación robusta
            result = solve_dos_fases_corregido(data.dict())
            print("✅ API Final: Dos Fases ejecutado exitosamente")
            return result
        
        elif data.method == "granm":
            if not GRANM_AVAILABLE:
                return {"error": "Método Gran M no disponible"}
            # Usar método Gran M
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
        return {"error": f"Error interno: {str(e)}"}

if __name__ == "__main__":
    print("🚀 Iniciando API Final Completa - Puerto 8003")
    print("✅ Implementación embedded del método Dos Fases")
    if GRANM_AVAILABLE:
        print("✅ Método Gran M disponible")
    else:
        print("⚠️ Método Gran M no disponible")
    uvicorn.run("api_final:app", host="0.0.0.0", port=8003, reload=False)
