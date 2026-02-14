"""
Test Overlay Always-On-Top
Verifica se o overlay fica por cima de outras janelas (incluindo jogos fullscreen)
"""
import sys
from src.ui.overlay import SROverlay
from PyQt6.QtWidgets import QApplication

def get_test_stats():
    """Retorna dados de teste para o overlay"""
    return {
        'current_sr': 4.85,
        'license_class': 'C',
        'license_color': '#FFAA00',
        'is_race_active': True,
        'incidents_1x': 2,
        'incidents_2x': 1,
        'incidents_4x': 0,
        'total_incidents': 3,
        'corners_completed': 87,
        'cpi': 29.0,
        'avg_incidents_per_corner': 0.034
    }

def main():
    print("=" * 70)
    print("TESTE DE OVERLAY - ALWAYS ON TOP")
    print("=" * 70)
    print()
    print("IMPORTANTE: O overlay NAO funciona em FULLSCREEN EXCLUSIVO!")
    print()
    print("Para usar com F1 2019:")
    print("  1. Abra F1 2019")
    print("  2. Settings -> Video -> Display Mode")
    print("  3. Mude para 'BORDERLESS WINDOW' (nao 'Fullscreen')")
    print("  4. Aplique e reinicie o jogo")
    print()
    print("Por que?")
    print("  * Fullscreen exclusivo = controle total da GPU pelo jogo")
    print("  * Windows nao pode renderizar outras janelas por cima")
    print("  * Borderless Window = mesma experiencia visual, overlay funciona!")
    print()
    print("=" * 70)
    print()
    print("Melhorias aplicadas no codigo:")
    print("  [OK] WindowStaysOnTopHint (Qt flag)")
    print("  [OK] WA_ShowWithoutActivating (nao rouba foco)")
    print("  [OK] SetWindowPos HWND_TOPMOST (Windows API)")
    print("  [OK] Timer para re-forcar a cada 1 segundo")
    print()
    print("Como testar AGORA:")
    print("  1. Deixe este overlay aberto")
    print("  2. Abra outras janelas (navegador, explorador de arquivos)")
    print("  3. O overlay deve ficar POR CIMA de todas elas")
    print()
    print("Como testar com F1 2019:")
    print("  1. Configure F1 2019 para BORDERLESS WINDOW (veja acima)")
    print("  2. Inicie o jogo")
    print("  3. O overlay deve aparecer por cima do jogo")
    print()
    print("Atalhos:")
    print("  Ctrl+Q: Esconder/Mostrar overlay")
    print("  Ctrl+M: Modo simples")
    print("  Ctrl++/-: Aumentar/Diminuir tamanho")
    print()
    print("=" * 70)
    print()
    
    app = QApplication(sys.argv)
    overlay = SROverlay(update_callback=get_test_stats)
    overlay.show()
    
    print("[OK] Overlay exibido!")
    print("Teste abrindo outras janelas - o overlay deve ficar no topo.")
    print("Feche a janela do overlay ou pressione Ctrl+C para sair.\n")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
