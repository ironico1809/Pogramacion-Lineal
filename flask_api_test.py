#!/usr/bin/env python3
"""
API de prueba usando Flask para verificar si el problema es específico de FastAPI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Configurar path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'components'))

from Metodo2F import SimplexDosFases
from MetodoM_NEW import SimplexTablaInicialCompleta

app = Flask(__name__)
CORS(app)  # Habilitar CORS

@app.route('/solve', methods=['POST'])
def solve_problem():
    try:
        data = request.get_json()
        
        print(f"🔍 FLASK API: Datos recibidos: {data}")
        
        if data.get("method") == "granm":
            # Usar método Gran M
            sm = SimplexTablaInicialCompleta()
            result = sm.solve_from_data(
                n_vars=data["n_vars"],
                n_cons=data["n_cons"],
                c=data["c"],
                A=data["A"],
                b=data["b"],
                signs=data["signs"],
                obj_type=data["obj_type"]
            )
        elif data.get("method") == "dosfases":
            # Usar método Dos Fases
            print("🔍 FLASK API: Creando SimplexDosFases")
            sm = SimplexDosFases()
            print("🔍 FLASK API: Llamando solve_from_data")
            result = sm.solve_from_data(
                n_vars=data["n_vars"],
                n_cons=data["n_cons"],
                c=data["c"],
                A=data["A"],
                b=data["b"],
                signs=data["signs"],
                obj_type=data["obj_type"]
            )
            print(f"🔍 FLASK API: Resultado obtenido")
        else:
            return jsonify({"error": "Método no soportado"}), 400
        
        print(f"✅ FLASK API: Enviando resultado")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ FLASK API: Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "message": "Flask API funcionando"})

if __name__ == '__main__':
    print("🚀 Iniciando Flask API en puerto 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)
