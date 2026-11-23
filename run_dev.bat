@echo off
setlocal
title SMOKECUT Backend Server (FastAPI)

cd /d "%~dp0"
set PYTHONPATH=.

echo =======================================================
echo   SMOKECUT Backend Server (FastAPI + CV Engine)
echo   Mode: Development (Auto-Reload Active)
echo   URL:  http://127.0.0.1:8000
echo   Docs: http://127.0.0.1:8000/docs
echo =======================================================
echo.

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
    echo [OK] Menggunakan Virtual Environment: venv
) else (
    set "PYTHON_EXE=python"
    echo [INFO] venv tidak ditemukan, menggunakan python global
)

:server_loop
echo.
echo [%date% %time%] Memulai server uvicorn...
"%PYTHON_EXE%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo [INFO] Server backend berhenti.
echo Restart otomatis dalam 3 detik (Tekan Ctrl+C untuk membatalkan)...
timeout /t 3 >nul
goto server_loop
