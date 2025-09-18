@echo off
echo ==========================================
echo   Executando Testes da API - FastAPI
echo ==========================================

echo.
echo [1] Instalando dependencias de teste...
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo [2] Executando todos os testes...
echo.
pytest tests/ -v --tb=short

echo.
echo ==========================================
echo Testes concluidos!
echo ==========================================
pause