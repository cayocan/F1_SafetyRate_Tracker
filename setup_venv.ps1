# Setup do Ambiente Virtual - F1 Safety Rating Tracker
# Este script cria o ambiente virtual e instala as dependências

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "F1 SAFETY RATING TRACKER - Setup do Ambiente Virtual" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Python está instalado
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python não encontrado. Por favor, instale o Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "      $pythonVersion" -ForegroundColor Green
Write-Host ""

# Criar ambiente virtual
Write-Host "[2/5] Criando ambiente virtual (.venv)..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "      Ambiente virtual já existe. Removendo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao criar ambiente virtual" -ForegroundColor Red
    exit 1
}
Write-Host "      Ambiente virtual criado com sucesso!" -ForegroundColor Green
Write-Host ""

# Ativar ambiente virtual
Write-Host "[3/5] Ativando ambiente virtual..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "AVISO: Falha ao ativar automaticamente. Ative manualmente com:" -ForegroundColor Yellow
    Write-Host "       .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
}
Write-Host "      Ambiente virtual ativado!" -ForegroundColor Green
Write-Host ""

# Atualizar pip
Write-Host "[4/5] Atualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "      pip atualizado!" -ForegroundColor Green
Write-Host ""

# Instalar dependências
Write-Host "[5/5] Instalando dependências..." -ForegroundColor Yellow
Write-Host "      - PyQt6" -ForegroundColor Cyan
Write-Host "      - Flask" -ForegroundColor Cyan
Write-Host "      - Werkzeug" -ForegroundColor Cyan
Write-Host ""
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao instalar dependências" -ForegroundColor Red
    exit 1
}
Write-Host ""
Write-Host "      Todas as dependências instaladas!" -ForegroundColor Green
Write-Host ""

# Verificar instalação
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Verificando instalação..." -ForegroundColor Yellow
Write-Host ""
python check_install.py

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SETUP CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Ativar o ambiente virtual (se não estiver ativado):" -ForegroundColor White
Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Executar o tracker:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Ou usar o script de ativação rápida:" -ForegroundColor White
Write-Host "   .\activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
