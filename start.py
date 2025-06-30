#!/usr/bin/env python3
"""
Script de inicio completo para el proyecto de Programación Lineal
Verifica dependencias e inicia el backend automáticamente
"""

import subprocess
import sys
import os

def install_requirements():
    """Instala las dependencias de Python si no están presentes"""
    print("🔧 Verificando dependencias de Python...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias de Python instaladas")
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias de Python")
        return False
    return True

def start_backend():
    """Inicia el servidor FastAPI"""
    print("🚀 Iniciando servidor backend...")
    try:
        # Cambiar al directorio del proyecto
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Iniciar uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.api.api:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Servidor backend detenido")
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")

def main():
    print("=" * 50)
    print("🎯 SOLVER DE PROGRAMACIÓN LINEAL")
    print("   Métodos: Gran M y Dos Fases")
    print("=" * 50)
    
    # Verificar si estamos en el directorio correcto
    if not os.path.exists("src/api/api.py"):
        print("❌ Error: No se encuentra el archivo src/api/api.py")
        print("   Asegúrate de ejecutar este script desde la raíz del proyecto")
        return
    
    # Instalar dependencias
    if not install_requirements():
        return
    
    print("\n📋 INSTRUCCIONES:")
    print("1. El backend se iniciará en http://localhost:8000")
    print("2. En otra terminal, ejecuta: npm run dev")
    print("3. Abre http://localhost:5173 en tu navegador")
    print("\n🔄 Iniciando backend...\n")
    
    # Iniciar backend
    start_backend()

if __name__ == "__main__":
    main()
