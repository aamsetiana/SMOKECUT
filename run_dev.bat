@echo off
setlocal
cd /d "%~dp0"
if /i "%~1"=="backend" goto backend

title SEKAT-AI Frontend (React)
echo =======================================================
echo   SEKAT-AI - Development
echo   Frontend : http://localhost:5173/react.html
echo   Backend  : http://127.0.0.1:8000  (docs: /docs)
echo   Tekan Ctrl+C di sini untuk menghentikan frontend.
echo   Tutup jendela "SEKAT-AI Backend" untuk menghentikan backend.
echo =======================================================
echo.

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js/npm tidak ditemukan. Instal dari https://nodejs.org
    pause
    exit /b 1
)

rem Pasang dependensi bila belum ada atau package-lock.json lebih baru (mis. setelah git pull)
set "NEED_INSTALL="
if not exist "frontend\node_modules\.package-lock.json" set "NEED_INSTALL=1"
if not defined NEED_INSTALL (
    xcopy /d /y /l "frontend\package-lock.json" "frontend\node_modules\.package-lock.json*" 2>nul | findstr /b /c:"1 " >nul && set "NEED_INSTALL=1"
)
if defined NEED_INSTALL (
    echo [INFO] Memasang dependensi frontend...
    call npm --prefix frontend ci
    if errorlevel 1 (
        echo [ERROR] npm ci gagal.
        pause
        exit /b 1
    )
)

netstat -ano | findstr /r /c:":8000 .*LISTENING" >nul
if errorlevel 1 (
    echo [INFO] Menjalankan backend di jendela terpisah...
    start "SEKAT-AI Backend" cmd /k ""%~f0" backend"
) else (
    echo [OK] Port 8000 sudah dipakai; memakai backend yang sedang berjalan.
)

cd frontend
call npm run dev -- --strictPort --open /react.html
if errorlevel 1 (
    echo.
    echo [ERROR] Frontend berhenti. Pastikan port 5173 tidak sedang dipakai.
    pause
)
exit /b

:backend
title SEKAT-AI Backend
set PYTHONPATH=.
set "PYTHON_EXE=python"
if exist "venv\Scripts\python.exe" set "PYTHON_EXE=venv\Scripts\python.exe"

:server_loop
echo [%date% %time%] Memulai server uvicorn...
"%PYTHON_EXE%" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir backend
echo.
echo [INFO] Backend berhenti. Restart dalam 3 detik (Ctrl+C untuk batal)...
timeout /t 3 >nul
goto server_loop
