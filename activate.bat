@echo off
REM Script de Ativação para CMD/Batch
REM Para usuários que preferem usar CMD ao invés de PowerShell

echo.
echo ========================================
echo Ativando Ambiente Virtual...
echo ========================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo.
    echo ========================================
    echo Ambiente Virtual ATIVADO!
    echo ========================================
    echo.
    echo Comandos disponiveis:
    echo   python main.py           - Iniciar o tracker
    echo   python check_install.py  - Verificar instalacao
    echo   python test_quick.py     - Executar testes
    echo   deactivate               - Desativar o ambiente
    echo.
    echo Dashboard Web: http://127.0.0.1:5000
    echo.
) else (
    echo.
    echo ERRO: Ambiente virtual nao encontrado!
    echo.
    echo Execute primeiro:
    echo   setup_venv.bat
    echo.
    pause
)
