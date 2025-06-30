@echo off
echo ====================================
echo    API COMPLETA - GRAN M + DOS FASES
echo ====================================
echo.
echo Iniciando servidor en puerto 8003...
echo.
cd /d "c:\Users\jerso\Documents\Programacion\Project"
call .venv\Scripts\activate.bat
echo Entorno virtual activado
echo.
echo Iniciando API (Ctrl+C para detener)...
python api_final.py
