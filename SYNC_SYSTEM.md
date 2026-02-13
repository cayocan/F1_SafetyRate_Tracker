# Sistema de Sincronização de Dados

## Arquitetura de Atualização

O F1 Safety Rate Tracker utiliza um sistema de sincronização em múltiplas camadas para garantir que todos os componentes exibam dados consistentes:

```
┌─────────────┐
│   F1 Game   │  UDP Port 20777
└──────┬──────┘
       │ Telemetry packets
       ▼
┌─────────────────────┐
│   SR Engine         │  Calcula SR em tempo real
│   (in-memory)       │  - CPI calculation
│                     │  - Boundary bonus
│                     │  - Incremental updates
└──────┬──────┬───────┘
       │      │
       │      └─────────────────────────────────┐
       │                                        │
       ▼                                        ▼
┌─────────────┐                        ┌──────────────┐
│   Overlay   │  100ms refresh         │  Database    │  2s sync
│   (PyQt6)   │  Real-time display     │  (SQLite)    │  During races
└─────────────┘                        └──────┬───────┘
                                               │
                                               │ Read every 2s
                                               ▼
                                       ┌────────────────┐
                                       │   Dashboard    │  2s refresh
                                       │   (Flask)      │  Web UI
                                       └────────────────┘
```

## Frequências de Atualização

### Overlay (PyQt6)
- **Frequência**: 100ms (10 Hz)
- **Fonte**: SR Engine (memória)
- **Responsividade**: Muito alta - mostra mudanças instantaneamente
- **Uso**: Feedback em tempo real durante corridas

### Database (SQLite)
- **Frequência**: 2 segundos durante corridas ativas
- **Método**: `_sync_sr_to_database_if_needed()` em `main.py`
- **Silencioso**: Não gera logs no console (evita spam)
- **Condição**: Apenas quando `self.is_race_active` é True

### Dashboard (Flask/HTML)
- **Frequência**: 2 segundos
- **Fonte**: Database via REST API
- **Endpoints atualizados**:
  - `/api/stats` - SR atual e estatísticas
  - `/api/history` - Histórico de sessões
  - `/api/sr-history` - Dados para gráfico
  - `/api/track-stats` - Estatísticas por pista
- **Indicador Visual**: "● LIVE (timestamp)" com animação de pulso

### System Tray
- **Frequência**: 5 segundos
- **Fonte**: SR Engine (memória)
- **Tooltip**: Mostra SR atual e classe de licença
- **Uso**: Info rápida sem abrir overlay ou dashboard

## Fluxo de Dados Durante uma Corrida

### 1. Telemetria Recebida (F1 Game)
```python
# main.py: _telemetry_loop()
packet = parser.parse_packet(data)
if packet:
    self._process_telemetry(packet)
```

### 2. Atualização do SR Engine
```python
# main.py: _process_telemetry()
if incident_detected:
    self.sr_engine.register_incident(...)
elif corner_completed:
    self.sr_engine.register_clean_corner()
```

### 3. Atualização do Overlay (100ms)
```python
# src/ui/overlay.py: _update_display()
self.sr_label.setText(f"{self.sr_engine.current_sr:.2f}")
# Atualiza automaticamente a cada 100ms
```

### 4. Sincronização com Database (2s)
```python
# main.py: _sync_sr_to_database_if_needed()
if current_time - self.last_db_sync_time >= self.db_sync_interval:
    self.database.update_sr(self.sr_engine.current_sr)
    self.last_db_sync_time = current_time
```

### 5. Atualização do Dashboard (2s)
```javascript
// index.html: loadStats()
setInterval(() => {
    loadStats();
    loadHistory();
    loadSRChart();
    loadTrackStats();
}, 2000);
```

## Garantia de Consistência

### Problema Anterior
- Database só atualizava no final da corrida
- Dashboard podia mostrar SR desatualizado
- Overlay e Dashboard mostravam valores diferentes

### Solução Implementada
1. **Sync Periódico**: Database atualiza a cada 2s durante corridas
2. **Refresh Unificado**: Dashboard atualiza TODOS os dados juntos
3. **Indicador Visual**: "● LIVE" mostra que está atualizando
4. **Timestamps**: Confirma quando foi a última atualização

### Casos de Uso

#### Corrida Ativa
- **Overlay**: Mostra SR em tempo real (100ms)
- **Database**: Sincroniza a cada 2s
- **Dashboard**: Atualiza a cada 2s (se aberto)
- **Resultado**: Máximo 2s de diferença entre componentes

#### Fora de Corrida
- **Overlay**: Mostra último valor do SR Engine
- **Database**: Não sincroniza (economiza recursos)
- **Dashboard**: Continua atualizando a cada 2s
- **Resultado**: Valores estáticos, todos sincronizados

#### Reset Manual
- **Ação**: Botão "Reset SR" no dashboard
- **Endpoint**: POST /api/reset-sr
- **Efeito**: Database → 2.50, próxima atualização sincroniza overlay

## Performance

### Impacto no CPU
- Overlay: ~1-2% (rendering PyQt6)
- Database sync: <0.1% (SQLite write cada 2s)
- Dashboard: <0.5% (Flask server idle)
- **Total**: ~2-3% CPU durante corridas

### Latência
- Incidente detectado → Overlay atualizado: <100ms
- SR mudou → Database atualizado: <2s
- Database atualizado → Dashboard mostra: <2s
- **Latência total (telemetria→dashboard)**: <4s

## Troubleshooting

### Dashboard não atualiza
1. Verificar se servidor Flask está rodando (porta 5000)
2. Abrir console do navegador (F12) - verificar erros de fetch
3. Verificar indicador "● LIVE" - deve pulsar a cada 2s

### Overlay e Dashboard mostram valores diferentes
1. Durante corrida: Diferença de até 2s é normal
2. Fora de corrida: Devem ser idênticos
3. Se persistir: Verificar logs no console do app

### Database não sincroniza
1. Verificar `self.is_race_active` em `main.py`
2. Conferir `last_db_sync_time` e `db_sync_interval`
3. Testar com `test_sync.py`

## Configuração

### Ajustar Frequências

```python
# main.py - Database sync
self.db_sync_interval = 2.0  # segundos (padrão: 2.0)

# src/ui/overlay.py - Overlay update
self.timer.setInterval(100)  # ms (padrão: 100)

# src/web/templates/index.html - Dashboard refresh
setInterval(loadStats, 2000);  # ms (padrão: 2000)
```

### Desabilitar Sync Durante Corridas
```python
# main.py: _telemetry_loop()
# Comentar esta linha:
# self._sync_sr_to_database_if_needed()
```

## Testes

### Teste de Sincronização
```bash
python test_sync.py
```
Verifica se SR Engine e Database mantêm valores idênticos.

### Teste do Dashboard
```bash
python test_dashboard.py
```
Testa se API retorna dados corretos e atualizados.

### Teste do System Tray
```bash
python test_system_tray.py
```
Verifica tooltip e atualização do ícone.

## Conclusão

O sistema de sincronização garante que:
- ✅ Overlay mostra feedback em tempo real
- ✅ Database mantém histórico preciso
- ✅ Dashboard exibe dados atualizados
- ✅ Todos os componentes convergem rapidamente
- ✅ Performance permanece otimizada
