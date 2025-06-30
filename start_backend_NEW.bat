@echo off
echo Iniciando servidor backend FastAPI...
echo.
cd /d "c:\Users\jerso\Documents\Programacion\Project"
echo Directorio actual: %CD%
echo.
python -m uvicorn src.api.api:app --host 0.0.0.0 --port 8000 --reload
pause
