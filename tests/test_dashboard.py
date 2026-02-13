"""
Teste rápido do Dashboard Web
Inicia o servidor Flask para verificar as mudanças
"""
import sys
from src.core.database import Database
from src.web.dashboard import Dashboard

def main():
    print("=" * 70)
    print("TESTE DO DASHBOARD WEB - F1 Safety Rating")
    print("=" * 70)
    print()
    
    # Conectar ao banco de dados
    db = Database()
    
    # Verificar SR atual
    current_sr = db.get_current_sr()
    print(f"Current SR: {current_sr:.2f}")
    
    # Criar e iniciar dashboard
    dashboard = Dashboard(database=db, host="127.0.0.1", port=5000)
    
    print()
    print("=" * 70)
    print("Dashboard Web Features:")
    print("  * Display SR com badge de classe de licença")
    print("  * Botão 'Reset to 2.50' com confirm dialog")
    print("  * Dados formatados corretamente (2 casas decimais)")
    print("  * Gráfico com escala 2.0-8.0 (nova escala iRacing)")
    print("=" * 70)
    print()
    print("Abrindo servidor em: http://127.0.0.1:5000")
    print("Pressione Ctrl+C para parar")
    print()
    
    try:
        dashboard.run(debug=False)
    except KeyboardInterrupt:
        print("\n\nServidor parado.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
