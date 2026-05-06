@echo off
TITLE Antigravity System - LLM Critica Oeste
echo ======================================================
echo   SISTEMA COMPLETO - LLM CRITICA OESTE
echo ======================================================
echo.

:: Iniciar Frontend em uma nova janela
echo [1/2] Iniciando Interface Web (Vite)...
start cmd /k "cd antigravity-ui && npm install && npm run dev"

:: Iniciar Backend em uma nova janela
echo [2/2] Iniciando Servidor de IA (FastAPI)...
start cmd /k "cd backend && pip install -r requirements.txt && python main.py"

echo.
echo ======================================================
echo   SISTEMA EM INICIALIZACAO!
echo   Frontend: http://localhost:5173
echo   Backend: http://localhost:8000
echo ======================================================
echo.
pause
