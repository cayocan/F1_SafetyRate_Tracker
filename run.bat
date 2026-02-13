@echo off
REM F1 Safety Rating Tracker - Launcher
REM Verifica ambiente, instala dependencias se necessario e executa o app

SETLOCAL EnableDelayedExpansion

echo.
echo ============================================================
echo F1 SAFETY RATING TRACKER - LAUNCHER
echo ============================================================
echo.

REM Verificar se Python esta instalado
echo [CHECK] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nao encontrado!
    echo.
    echo Por favor, instale o Python 3.8+ de:
    echo https://www.python.org/downloads/
    echo.
    echo Certifique-se de marcar "Add Python to PATH" durante a instalacao!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% encontrado
echo.

REM Verificar se o ambiente virtual existe
echo [CHECK] Verificando ambiente virtual...
if not exist ".venv" (
    echo [INFO] Ambiente virtual nao encontrado. Criando...
    echo.
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado!
    echo.
    set NEED_INSTALL=1
) else (
    echo [OK] Ambiente virtual existe
    echo.
    set NEED_INSTALL=0
)

REM Ativar ambiente virtual
echo [CHECK] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Falha ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo [OK] Ambiente ativado
echo.

REM Verificar se pip precisa ser atualizado
echo [CHECK] Verificando pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip atualizado
echo.

REM Verificar dependencias
echo [CHECK] Verificando dependencias...
python -c "import PyQt6.QtWidgets; import flask; import werkzeug" 2>nul
if errorlevel 1 (
    echo [INFO] Dependencias faltando ou desatualizadas. Instalando...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Falha ao instalar dependencias!
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas!
    echo.
) else (
    if !NEED_INSTALL!==1 (
        echo [INFO] Instalando dependencias...
        echo.
        pip install -r requirements.txt --quiet
        echo [OK] Dependencias instaladas!
        echo.
    ) else (
        echo [OK] Todas as dependencias estao instaladas
        echo.
    )
)

REM Verificacao rapida final
echo [CHECK] Verificacao final do sistema...
python -c "import PyQt6.QtWidgets; import flask; import werkzeug; print('OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] Alguns componentes podem estar com problemas
    echo [INFO] Executando verificacao detalhada...
    echo.
    python check_install.py
    echo.
    echo Deseja continuar mesmo assim? (S/N)
    set /p CONTINUE=
    if /i "!CONTINUE!" neq "S" (
        echo Abortando...
        pause
        exit /b 0
    )
) else (
    echo [OK] Sistema operacional!
)

echo.
echo ============================================================
echo INICIANDO F1 SAFETY RATING TRACKER
echo ============================================================
echo.
echo [INFO] Aplicacao iniciando...
echo [INFO] Dashboard Web: http://127.0.0.1:5000
echo [INFO] Pressione Ctrl+C para encerrar
echo.
echo ------------------------------------------------------------
echo.

REM Executar o aplicativo
python main.py

REM Se o app encerrar normalmente
echo.
echo.
echo ============================================================
echo APLICACAO ENCERRADA
echo ============================================================
echo.

REM Desativar ambiente virtual
call deactivate 2>nul

pause
