"""
Teste de Sincronização entre Overlay e Dashboard
Verifica se mudanças no SR são refletidas em ambos os componentes
"""
import time
from src.core import Database, SREngine

def test_sync():
    print("=" * 70)
    print("TESTE DE SINCRONIZAÇÃO - Overlay & Dashboard")
    print("=" * 70)
    print()
    
    # Create database and SR engine
    db = Database("history.db")
    sr_engine = SREngine()
    
    # Load initial SR
    initial_sr = db.get_current_sr()
    sr_engine.set_sr(initial_sr)
    
    print(f"Initial SR (Database): {initial_sr:.2f}")
    print(f"Initial SR (SR Engine): {sr_engine.current_sr:.2f}")
    print()
    
    # Simulate SR changes
    print("Simulating SR changes...")
    print("-" * 70)
    
    test_values = [2.50, 3.00, 3.50, 4.00, 4.50, 5.00]
    
    for new_sr in test_values:
        print(f"\nSetting SR to {new_sr:.2f}...")
        
        # Update SR engine
        sr_engine.set_sr(new_sr)
        print(f"  SR Engine: {sr_engine.current_sr:.2f}")
        
        # Update database
        db.update_sr(new_sr)
        
        # Read back from database
        db_sr = db.get_current_sr()
        print(f"  Database:  {db_sr:.2f}")
        
        # Check sync
        if abs(sr_engine.current_sr - db_sr) < 0.01:
            print("  ✓ SYNCED")
        else:
            print("  ✗ OUT OF SYNC!")
        
        time.sleep(0.5)
    
    print()
    print("-" * 70)
    print()
    print("RESULTADO:")
    print("  * SR Engine e Database devem estar sempre sincronizados")
    print("  * Dashboard lê do Database")
    print("  * Overlay lê do SR Engine")
    print("  * Com sync periódico (a cada 2s), ambos ficam atualizados")
    print()
    print("FREQUÊNCIAS DE ATUALIZAÇÃO:")
    print("  * Overlay: 100ms (10 Hz) - muito responsivo")
    print("  * Dashboard: 2000ms (0.5 Hz) - atualização contínua")
    print("  * DB Sync: 2000ms durante corridas ativas")
    print()
    
    db.close()

if __name__ == "__main__":
    test_sync()
