import subprocess
import time
import requests
import json
import threading

def start_server():
    """Iniciar el servidor en un hilo separado."""
    try:
        subprocess.run(["python", "api_final.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error iniciando servidor: {e}")

def test_dos_fases_directo():
    """Probar el método de Dos Fases directamente."""
    # Iniciar servidor en background
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Esperar un momento para que el servidor inicie
    print("Esperando que el servidor inicie...")
    time.sleep(3)
    
    # Probar la API
    url = "http://localhost:8003/solve"
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
    
    print("=== PROBANDO DOS FASES CON SERVIDOR REINICIADO ===")
    print("Payload:", json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        print(f"Status HTTP: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                print(f"❌ ERROR: {data['error']}")
            else:
                print("✅ ÉXITO - Dos Fases funcionó!")
                if 'fase2' in data and 'solucion' in data['fase2']:
                    print(f"📊 Solución: {data['fase2']['solucion']}")
                if 'fase2' in data and 'valor_objetivo' in data['fase2']:
                    print(f"💰 Valor objetivo: {data['fase2']['valor_objetivo']}")
        else:
            print("❌ Error HTTP:")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose en el puerto 8003?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dos_fases_directo()
