@echo off
REM Setup do Ambiente Virtual para CMD/Batch

echo ============================================================
echo F1 SAFETY RATING TRACKER - Setup do Ambiente Virtual
echo ============================================================
echo.

REM Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado. Instale o Python 3.8+
    pause
    exit /b 1
)
python --version
echo.

REM Criar ambiente virtual
echo [2/5] Criando ambiente virtual (.venv)...
if exist .venv (
    echo       Ambiente virtual ja existe. Removendo...
    rmdir /s /q .venv
)
python -m venv .venv
if errorlevel 1 (
    echo ERRO: Falha ao criar ambiente virtual
    pause
    exit /b 1
)
echo       Ambiente virtual criado com sucesso!
echo.

REM Ativar ambiente virtual
echo [3/5] Ativando ambiente virtual...
call .venv\Scripts\activate.bat
echo       Ambiente virtual ativado!
echo.

REM Atualizar pip
echo [4/5] Atualizando pip...
python -m pip install --upgrade pip --quiet
echo       pip atualizado!
echo.

REM Instalar dependências
echo [5/5] Instalando dependencias...
echo       - PyQt6
echo       - Flask
echo       - Werkzeug
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)
echo.
echo       Todas as dependencias instaladas!
echo.

REM Verificar instalação
echo ============================================================
echo Verificando instalacao...
echo.
python check_install.py

echo.
echo ============================================================
echo SETUP CONCLUIDO COM SUCESSO!
echo ============================================================
echo.
echo Proximos passos:
echo.
echo 1. Ativar o ambiente virtual:
echo    activate.bat  OU  .venv\Scripts\activate.bat
echo.
echo 2. Executar o tracker:
echo    python main.py
echo.
echo ============================================================
echo.
pause
