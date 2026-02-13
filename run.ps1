# F1 Safety Rating Tracker - Quick Launcher
# PowerShell version of the launcher script

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    
    switch ($Type) {
        "ERROR" { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "OK"    { Write-Host "[OK] $Message" -ForegroundColor Green }
        "INFO"  { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
        "CHECK" { Write-Host "[CHECK] $Message" -ForegroundColor Yellow }
        "WARN"  { Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "F1 SAFETY RATING TRACKER - LAUNCHER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Status "Verificando Python..." "CHECK"
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw }
    Write-Status "Python $pythonVersion encontrado" "OK"
} catch {
    Write-Status "Python não encontrado!" "ERROR"
    Write-Host ""
    Write-Host "Por favor, instale o Python 3.8+ de:"
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Certifique-se de marcar 'Add Python to PATH' durante a instalação!"
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host ""

# Verificar ambiente virtual
Write-Status "Verificando ambiente virtual..." "CHECK"
$needInstall = $false
if (-not (Test-Path ".venv")) {
    Write-Status "Ambiente virtual não encontrado. Criando..." "INFO"
    Write-Host ""
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Falha ao criar ambiente virtual!" "ERROR"
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    Write-Status "Ambiente virtual criado!" "OK"
    $needInstall = $true
} else {
    Write-Status "Ambiente virtual existe" "OK"
}
Write-Host ""

# Ativar ambiente virtual
Write-Status "Ativando ambiente virtual..." "CHECK"
try {
    & .venv\Scripts\Activate.ps1
    Write-Status "Ambiente ativado" "OK"
} catch {
    Write-Status "Falha ao ativar ambiente virtual!" "ERROR"
    Write-Host ""
    Write-Host "Se encontrar erro de Execution Policy, execute:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}
Write-Host ""

# Atualizar pip
Write-Status "Verificando pip..." "CHECK"
python -m pip install --upgrade pip --quiet
Write-Status "pip atualizado" "OK"
Write-Host ""

# Verificar dependências
Write-Status "Verificando dependências..." "CHECK"
$dependenciesOk = python -c "import PyQt6.QtWidgets; import flask; import werkzeug" 2>$null
if ($LASTEXITCODE -ne 0 -or $needInstall) {
    Write-Status "Instalando dependências..." "INFO"
    Write-Host ""
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Status "Falha ao instalar dependências!" "ERROR"
        Read-Host "Pressione Enter para sair"
        exit 1
    }
    Write-Status "Dependências instaladas!" "OK"
} else {
    Write-Status "Todas as dependências estão instaladas" "OK"
}
Write-Host ""

# Verificação final
Write-Status "Verificação final do sistema..." "CHECK"
$checkResult = python -c "import PyQt6.QtWidgets; import flask; import werkzeug; print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Status "Alguns componentes podem estar com problemas" "WARN"
    Write-Status "Executando verificação detalhada..." "INFO"
    Write-Host ""
    python check_install.py
    Write-Host ""
    $continue = Read-Host "Deseja continuar mesmo assim? (S/N)"
    if ($continue -ne "S" -and $continue -ne "s") {
        Write-Host "Abortando..."
        exit 0
    }
} else {
    Write-Status "Sistema operacional!" "OK"
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INICIANDO F1 SAFETY RATING TRACKER" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Status "Aplicação iniciando..." "INFO"
Write-Status "Dashboard Web: http://127.0.0.1:5000" "INFO"
Write-Status "Pressione Ctrl+C para encerrar" "INFO"
Write-Host ""
Write-Host "------------------------------------------------------------"
Write-Host ""

# Executar aplicativo
try {
    python main.py
} catch {
    Write-Status "Aplicação encerrada com erro" "ERROR"
} finally {
    Write-Host ""
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "APLICAÇÃO ENCERRADA" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
}

# Desativar ambiente
deactivate 2>$null

Read-Host "Pressione Enter para sair"
