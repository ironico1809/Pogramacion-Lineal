import subprocess
import time
import requests
import json
import os
import signal

def force_restart_and_test():
    """Forzar reinicio del servidor y probar."""
    
    print("=== FORZANDO REINICIO COMPLETO ===")
    
    # 1. Terminar todos los procesos Python
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, text=True)
        print("✅ Procesos Python terminados")
    except:
        print("⚠️ No se pudieron terminar procesos Python")
    
    time.sleep(2)
    
    # 2. Iniciar el servidor en background
    print("🚀 Iniciando servidor...")
    
    try:
        # Iniciar el servidor usando subprocess
        server_process = subprocess.Popen(
            ["python", "api_final.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Dar tiempo para que inicie
        time.sleep(5)
        
        # 3. Verificar que el servidor está corriendo
        try:
            response = requests.get("http://localhost:8003/", timeout=5)
            print("✅ Servidor iniciado correctamente")
        except:
            print("❌ Servidor no responde")
            return
        
        # 4. Probar el método de Dos Fases
        print("\n=== PROBANDO DOS FASES CON SERVIDOR REINICIADO ===")
        
        payload = {
            "method": "dosfases",
            "n_vars": 2,
            "n_cons": 2,
            "c": [2000, 500],
            "A": [[2, 3], [3, 6]],
            "b": [36, 60],
            "signs": [">=", ">="],
            "obj_type": "min"
        }
        
        response = requests.post(
            "http://localhost:8003/solve",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ ERROR: {data['error']}")
                print("El servidor aún no usa la versión corregida")
            else:
                print("✅ ÉXITO - Dos Fases funcionó!")
                print(f"📊 Solución: {data['fase2']['solucion']}")
                print(f"💰 Valor objetivo: {data['fase2']['valor_objetivo']}")
                print("🎉 ¡PROBLEMA RESUELTO!")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Terminar el servidor
        try:
            server_process.terminate()
            print("\n🛑 Servidor terminado")
        except:
            pass

if __name__ == "__main__":
    force_restart_and_test()
