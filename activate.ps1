# Script de Ativação Rápida do Ambiente Virtual
# Ativa o .venv e mostra informações úteis

# Ativar ambiente virtual
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Ambiente Virtual ATIVADO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Python: $(python --version)" -ForegroundColor Cyan
    Write-Host "Localização: $((Get-Command python).Source)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Comandos disponíveis:" -ForegroundColor Yellow
    Write-Host "  python main.py           - Iniciar o tracker" -ForegroundColor White
    Write-Host "  python check_install.py  - Verificar instalação" -ForegroundColor White
    Write-Host "  python test_quick.py     - Executar testes" -ForegroundColor White
    Write-Host "  python demo_simulation.py - Simulação sem o jogo" -ForegroundColor White
    Write-Host "  deactivate               - Desativar o ambiente" -ForegroundColor White
    Write-Host ""
    Write-Host "Dashboard Web: http://127.0.0.1:5000" -ForegroundColor Magenta
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERRO: Ambiente virtual não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Execute primeiro:" -ForegroundColor Yellow
    Write-Host "  .\setup_venv.ps1" -ForegroundColor Cyan
    Write-Host ""
}
