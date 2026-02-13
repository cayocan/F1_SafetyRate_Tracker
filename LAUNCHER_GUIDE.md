# 🚀 Quick Launcher Guide

## What is `run.bat` / `run.ps1`?

**One-click launcher** that automatically:
- ✅ Checks if Python is installed
- ✅ Creates the virtual environment if missing
- ✅ Installs/updates all dependencies
- ✅ Runs system verification
- ✅ Launches the F1 Safety Rating Tracker

## How to Use

### Windows (CMD/Batch)
Simply **double-click** `run.bat` or run:
```batch
run.bat
```

### Windows (PowerShell)
```powershell
.\run.ps1
```

> **Note:** If you get an execution policy error in PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

## What Happens When You Run It?

### 1. System Check Phase
```
[CHECK] Verificando Python...
[OK] Python 3.11.9 encontrado

[CHECK] Verificando ambiente virtual...
[OK] Ambiente virtual existe

[CHECK] Ativando ambiente virtual...
[OK] Ambiente ativado
```

### 2. Dependency Installation (if needed)
```
[CHECK] Verificando dependências...
[INFO] Instalando dependências...
[OK] Dependências instaladas!
```

### 3. Final Verification
```
[CHECK] Verificação final do sistema...
[OK] Sistema operacional!
```

### 4. Application Launch
```
============================================================
INICIANDO F1 SAFETY RATING TRACKER
============================================================

[INFO] Aplicação iniciando...
[INFO] Dashboard Web: http://127.0.0.1:5000
[INFO] Pressione Ctrl+C para encerrar
```

## First-Time Setup

If this is your **first time** running the tracker:
1. The script will automatically create `.venv/` folder
2. Install all dependencies (PyQt6, Flask, etc.)
3. Run verification checks
4. Start the application

**Total time:** ~30-60 seconds (depending on internet speed)

## Subsequent Runs

On future runs:
1. Quick environment check (~1 second)
2. Verify dependencies are up-to-date
3. Launch immediately

**Total time:** ~2-5 seconds

## Troubleshooting

### Python Not Found
```
[ERROR] Python não encontrado!

Por favor, instale o Python 3.8+ de:
https://www.python.org/downloads/
```

**Solution:** Install Python 3.8+ and make sure to check **"Add Python to PATH"** during installation.

### Dependency Installation Fails
```
[ERROR] Falha ao instalar dependências!
```

**Solutions:**
1. Check your internet connection
2. Update pip: `python -m pip install --upgrade pip`
3. Try manual installation:
   ```batch
   .\activate.ps1
   pip install -r requirements.txt
   ```

### System Check Warnings
```
[WARNING] Alguns componentes podem estar com problemas
Deseja continuar mesmo assim? (S/N)
```

**What to do:**
- Press **S** to continue anyway (usually safe for minor warnings)
- Press **N** to abort and check the detailed error output

### Execution Policy Error (PowerShell)
```
File cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Comparison with Other Methods

| Method | Setup Time | Best For |
|--------|------------|----------|
| `run.bat` / `run.ps1` | **Auto** | Daily use, newcomers |
| `.\activate.ps1` + `python main.py` | Manual | Advanced users |
| `.\setup_venv.ps1` | One-time | Initial setup only |

## Technical Details

### What Gets Installed?
- **PyQt6** (6.4.0+) - Real-time overlay UI
- **Flask** (2.3.0+) - Web dashboard server
- **Werkzeug** (2.3.0+) - WSGI utilities
- **colorama** (0.4.6+) - Colored terminal output

### Environment Variables
The launcher automatically:
- Activates `.venv\Scripts\activate.bat`
- Sets Python path to `.venv\Scripts\python.exe`
- Deactivates environment on exit

### Exit Codes
- **0** - Success (normal exit)
- **1** - Error (check error message)

## Clean Uninstall

To remove everything:
```batch
REM Delete virtual environment
rmdir /s /q .venv

REM Delete database (optional - removes your SR history!)
del history.db
```

Then re-run `run.bat` to start fresh.

---

## Quick Reference

```batch
# Launch everything (recommended)
run.bat

# Manual launch
.\activate.ps1
python main.py

# Full reinstall
rmdir /s /q .venv
run.bat
```

**Need Help?** Check the main [README.md](README.md) for detailed documentation.
