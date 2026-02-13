"""
Teste rápido dos componentes principais
"""
import os
import sys

print("=" * 60)
print("TESTE RÁPIDO DOS COMPONENTES")
print("=" * 60)

# Teste 1: Database
print("\n[1/5] Testando Database...")
try:
    from src.core import Database
    
    # Criar DB de teste
    test_db = "test_history.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    db = Database(test_db)
    
    # Testar operações básicas
    sr = db.get_current_sr()
    assert sr == 100.0, "SR inicial deveria ser 100.0"
    
    # Testar atualização de SR
    db.update_sr(95.5)
    sr = db.get_current_sr()
    assert sr == 95.5, "SR atualizado deveria ser 95.5"
    
    # Testar tracks
    track = db.get_track_by_game_id(16)
    assert track is not None, "Track 16 (Interlagos) deveria existir"
    assert "Brazil" in track['name'] or "Interlagos" in track['name']
    
    db.close()
    os.remove(test_db)
    
    print("   ✅ Database OK")
except Exception as e:
    print(f"   ❌ Erro no Database: {e}")
    sys.exit(1)

# Teste 2: SR Engine
print("\n[2/5] Testando SR Engine...")
try:
    from src.core import SREngine
    from src.adapters.base_adapter import RaceState
    import time
    
    engine = SREngine(window_size=10, sr_multiplier=10.0)
    
    # Testar estado inicial
    stats = engine.get_stats()
    assert stats['current_sr'] == 100.0, "SR inicial deveria ser 100.0"
    assert stats['total_incidents'] == 0, "Incidentes iniciais deveriam ser 0"
    
    # Simular telemetria limpa (sem incidentes)
    state = RaceState(
        session_uid=12345,
        session_type=10,
        session_time=60.0,
        game_paused=False,
        track_id=16,
        current_lap=1,
        is_off_track=False,
        front_left_damage=0.0,
        front_right_damage=0.0,
        rear_left_damage=0.0,
        rear_right_damage=0.0,
        timestamp=time.time()
    )
    
    engine.process_telemetry(state)
    stats = engine.get_stats()
    assert stats['current_sr'] == 100.0, "SR deveria permanecer 100.0 sem incidentes"
    
    print("   ✅ SR Engine OK")
except Exception as e:
    print(f"   ❌ Erro no SR Engine: {e}")
    sys.exit(1)

# Teste 3: Session Manager
print("\n[3/5] Testando Session Manager...")
try:
    from src.core import SessionManager
    
    race_started = False
    race_ended = False
    
    def on_start(uid, track, sr):
        global race_started
        race_started = True
    
    def on_end(uid, sr):
        global race_ended
        race_ended = True
    
    manager = SessionManager(on_race_start=on_start, on_race_end=on_end)
    
    # Testar estado inicial
    assert not manager.is_race_active(), "Corrida não deveria estar ativa"
    
    # Simular início de corrida
    state = RaceState(
        session_uid=99999,
        session_type=10,  # Race
        session_time=10.0,
        game_paused=False,
        track_id=16,
        current_lap=1,
        is_off_track=False,
        front_left_damage=0.0,
        front_right_damage=0.0,
        rear_left_damage=0.0,
        rear_right_damage=0.0,
        timestamp=time.time()
    )
    
    manager.process_telemetry(state)
    assert race_started, "Callback de início deveria ter sido chamado"
    assert manager.is_race_active(), "Corrida deveria estar ativa"
    
    print("   ✅ Session Manager OK")
except Exception as e:
    print(f"   ❌ Erro no Session Manager: {e}")
    sys.exit(1)

# Teste 4: F1 2019 Adapter
print("\n[4/5] Testando F1 2019 Adapter...")
try:
    from src.adapters import F12019Adapter
    
    adapter = F12019Adapter()
    assert adapter.get_game_version() == "F1 2019"
    
    # Testar parse de pacote inválido
    result = adapter.parse_packet(b"invalid")
    assert result is None, "Pacote inválido deveria retornar None"
    
    print("   ✅ F1 2019 Adapter OK")
except Exception as e:
    print(f"   ❌ Erro no Adapter: {e}")
    sys.exit(1)

# Teste 5: Imports do UI e Web
print("\n[5/5] Testando imports UI e Web...")
try:
    # Tentar importar overlay (pode falhar se PyQt6 não estiver configurado)
    try:
        import importlib.util
        spec = importlib.util.find_spec("src.ui.overlay")
        if spec is not None:
            from src.ui import overlay as _  # noqa: F401
            print("   ✅ UI (PyQt6) OK")
        else:
            print("   ⚠️  UI (PyQt6) não disponível")
    except ImportError as e:
        print(f"   ⚠️  UI (PyQt6) não disponível: {e}")
    
    # Tentar importar dashboard
    try:
        import importlib.util
        spec = importlib.util.find_spec("src.web.dashboard")
        if spec is not None:
            from src.web import dashboard as _  # noqa: F401
            print("   ✅ Web (Flask) OK")
        else:
            print("   ⚠️  Web (Flask) não disponível")
    except ImportError as e:
        print(f"   ⚠️  Web (Flask) não disponível: {e}")
    
except Exception as e:
    print(f"   ❌ Erro nos imports: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print("\nO sistema está pronto para uso!")
print("Execute: python main.py")
