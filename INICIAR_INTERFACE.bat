@echo off
TITLE Inicializando Antigravity UI - LLM Critica Oeste
echo ======================================================
echo   INICIALIZANDO INTERFACE PREMIUM - ANTIGRAVITY
echo ======================================================
echo.

cd antigravity-ui

echo [1/2] Instalando dependencias (isso pode demorar um pouco)...
call npm install

echo.
echo [2/2] Iniciando servidor de desenvolvimento...
echo A interface abrira automaticamente em instantes.
echo.

start http://localhost:5173
call npm run dev

pause
