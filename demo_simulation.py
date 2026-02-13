"""
Demo Simulation - F1 Safety Rating Tracker
Simula telemetria do F1 2019 para demonstração sem o jogo
"""
import struct
import socket
import time
import random

def create_f1_2019_packet(packet_id, session_uid, session_time, player_index=0):
    """
    Cria um pacote F1 2019 simulado
    
    packet_id:
    - 1 = Session
    - 2 = Lap Data  
    - 6 = Car Damage
    """
    # Header (24 bytes)
    packet_format = 2019
    game_major = 1
    game_minor = 0
    packet_version = 1
    
    header = struct.pack('<HBBBBQfIB',
                        packet_format,
                        game_major,
                        game_minor,
                        packet_version,
                        packet_id,
                        session_uid,
                        session_time,
                        0,  # frame identifier
                        player_index
    )
    
    # Payload depende do tipo de pacote
    if packet_id == 1:  # Session packet
        # Session type + track ID + game paused
        payload = struct.pack('<B', 10)  # Session type = 10 (Race)
        payload += struct.pack('<b', 16)  # Track ID = 16 (Interlagos)
        payload += b'\x00' * 213  # Padding até byte 239
        payload += struct.pack('<B', 0)  # Game not paused
        
    elif packet_id == 2:  # Lap Data packet
        # 20 cars * 41 bytes each
        lap_data = struct.pack('<ffffffffBBBBBBBBB',
                              0.0,  # lastLapTime
                              session_time,  # currentLapTime
                              0.0,  # bestLapTime
                              0.0, 0.0, 0.0, 0.0, 0.0,  # sectors, distances, delta
                              1,  # carPosition
                              1,  # currentLapNum
                              0,  # pitStatus
                              0,  # sector
                              0,  # currentLapInvalid (0 = valid)
                              0,  # penalties
                              1,  # gridPosition
                              2,  # driverStatus (racing)
                              0   # resultStatus
        )
        payload = lap_data + (b'\x00' * 41 * 19)  # Player + 19 other cars
        
    elif packet_id == 6:  # Car Damage packet
        # 20 cars * 39 bytes each
        damage_data = struct.pack('<ffffBBBBBBBBBBBB',
                                 0.0, 0.0, 0.0, 0.0,  # tyre wear
                                 0, 0, 0, 0,  # tyre damage
                                 0, 0, 0, 0,  # brake damage
                                 0,  # front left wing
                                 0,  # front right wing
                                 0,  # rear wing
                                 0   # engine
        )
        payload = damage_data + (b'\x00' * 39 * 19)
    else:
        payload = b''
    
    return header + payload


def simulate_clean_race(duration_seconds=30):
    """Simula uma corrida limpa (sem incidentes)"""
    print("🏁 Simulando corrida LIMPA (sem incidentes)")
    print("   Duração: {}s".format(duration_seconds))
    print("   Porta: 20777")
    print()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    session_uid = random.randint(100000, 999999)
    session_time = 0.0
    current_lap = 1
    
    start_time = time.time()
    
    print("[Simulação] Iniciando corrida...")
    
    while (time.time() - start_time) < duration_seconds:
        session_time = time.time() - start_time
        
        # Enviar pacote de sessão
        packet = create_f1_2019_packet(1, session_uid, session_time)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Enviar pacote de lap data
        packet = create_f1_2019_packet(2, session_uid, session_time)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Enviar pacote de dano
        packet = create_f1_2019_packet(6, session_uid, session_time)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Mudar de volta a cada 10 segundos
        if int(session_time) % 10 == 0 and int(session_time) > 0:
            current_lap += 1
            print(f"[Simulação] Volta {current_lap} - Tempo: {session_time:.1f}s")
        
        time.sleep(0.1)  # 10Hz
    
    print(f"[Simulação] Corrida finalizada após {duration_seconds}s")
    print()
    
    sock.close()


def simulate_race_with_incidents(duration_seconds=30, incident_rate=0.1):
    """Simula uma corrida com incidentes (off-tracks)"""
    print("⚠️  Simulando corrida COM INCIDENTES")
    print(f"   Duração: {duration_seconds}s")
    print(f"   Taxa de incidentes: {incident_rate*100:.0f}%")
    print("   Porta: 20777")
    print()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    session_uid = random.randint(100000, 999999)
    session_time = 0.0
    current_lap = 1
    incident_count = 0
    
    start_time = time.time()
    
    print("[Simulação] Iniciando corrida...")
    
    while (time.time() - start_time) < duration_seconds:
        session_time = time.time() - start_time
        
        # Enviar pacote de sessão
        packet = create_f1_2019_packet(1, session_uid, session_time)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Simular off-track aleatoriamente
        is_off_track = random.random() < incident_rate
        
        if is_off_track:
            incident_count += 1
            print(f"[Simulação] 💥 Incidente! (Total: {incident_count})")
        
        # Criar pacote de lap data modificado para simular off-track
        header = struct.pack('<HBBBBQfIB', 2019, 1, 0, 1, 2, session_uid, session_time, 0, 0)
        lap_data = struct.pack('<ffffffffBBBBBBBBB',
                              0.0, session_time, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                              1, current_lap, 0, 0,
                              1 if is_off_track else 0,  # currentLapInvalid
                              0, 1, 2, 0
        )
        packet = header + lap_data + (b'\x00' * 41 * 19)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Enviar pacote de dano
        packet = create_f1_2019_packet(6, session_uid, session_time)
        sock.sendto(packet, ('127.0.0.1', 20777))
        
        # Mudar de volta
        if int(session_time) % 10 == 0 and int(session_time) > 0:
            current_lap += 1
            print(f"[Simulação] Volta {current_lap} - Tempo: {session_time:.1f}s - Incidentes: {incident_count}")
        
        time.sleep(0.1)
    
    print(f"[Simulação] Corrida finalizada - Total de incidentes: {incident_count}")
    print()
    
    sock.close()


def main():
    print("=" * 60)
    print("F1 2019 SAFETY RATING TRACKER - SIMULATION DEMO")
    print("=" * 60)
    print()
    print("Este script simula telemetria do F1 2019 para demonstração.")
    print()
    print("IMPORTANTE:")
    print("1. Certifique-se de que o tracker está rodando:")
    print("   python main.py")
    print()
    print("2. Este script enviará pacotes UDP simulados na porta 20777")
    print()
    print("=" * 60)
    print()
    
    input("Pressione ENTER para iniciar a simulação...")
    print()
    
    # Simulação 1: Corrida limpa
    print("\n" + "=" * 60)
    simulate_clean_race(duration_seconds=20)
    
    print("Aguardando 3 segundos...")
    time.sleep(3)
    
    # Simulação 2: Corrida com incidentes
    print("\n" + "=" * 60)
    simulate_race_with_incidents(duration_seconds=20, incident_rate=0.15)
    
    print("=" * 60)
    print("✅ Simulação concluída!")
    print()
    print("Verifique:")
    print("- Overlay: SR deveria ter diminuído na segunda corrida")
    print("- Dashboard: http://127.0.0.1:5000 para ver histórico")
    print("=" * 60)


if __name__ == "__main__":
    main()
