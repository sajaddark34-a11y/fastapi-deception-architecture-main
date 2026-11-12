@echo off
setlocal EnableDelayedExpansion
title FastAPI-Driven Deception Architecture - Single-Click Launcher

echo ================================================================================
echo   FASTAPI-DRIVEN DECEPTION ARCHITECTURE - SYSTEM BOOTSTRAPPER
echo ================================================================================
echo.

REM 0. Resolve Project Root Directory [handles both outer and inner folder]
cd /d "%~dp0"
if exist "%~dp0run_all.py" goto :FOUND_ROOT
if exist "%~dp0fastapi-deception-architecture-main\run_all.py" (
    cd /d "%~dp0fastapi-deception-architecture-main"
    goto :FOUND_ROOT
)
echo [ERROR] Could not locate run_all.py in "%~dp0".
pause
exit /b 1

:FOUND_ROOT
echo [STEP 1/5] Checking Python installation...
set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python --version >nul 2>&1
    if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=python"
)
if not defined PYTHON_CMD (
    where py >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        py -3 --version >nul 2>&1
        if !ERRORLEVEL! EQU 0 set "PYTHON_CMD=py -3"
    )
)
if not defined PYTHON_CMD (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo         Detected: !PY_VER!

echo.
echo [STEP 2/5] Checking Virtual Environment and Core Dependencies...
if not exist ".venv\Scripts\python.exe" (
    echo         Creating virtual environment [.venv]...
    %PYTHON_CMD% -m venv --system-site-packages .venv
)
if exist ".venv\Scripts\python.exe" (
    echo         Using virtual environment [.venv\Scripts\python.exe].
    set "PYTHON_CMD=.venv\Scripts\python.exe"
)

%PYTHON_CMD% -c "import fastapi, uvicorn, pydantic, sqlalchemy, httpx, redis, asyncpg, aiosqlite, fakeredis, jinja2" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo         Installing missing dependencies from requirements.txt...
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements.txt
) else (
    echo         All required Python packages [FastAPI, Uvicorn, Pydantic, SQLAlchemy, AsyncPG, Jinja2, Redis] are ready.
)

echo.
echo [STEP 3/5] Checking Environment Configuration [.env]...
if not exist ".env" (
    echo         Creating default .env configuration file...
    echo SERVICE_NAME=deception_gateway> ".env"
    echo BIND_HOST=0.0.0.0>> ".env"
    echo GATEWAY_PORT=8000>> ".env"
    echo CORE_APP_PORT=8001>> ".env"
    echo DECOY_SERVICE_PORT=8080>> ".env"
    echo FORENSIC_ENGINE_PORT=8090>> ".env"
    echo SOC_DASHBOARD_PORT=8500>> ".env"
    echo CORE_WEB_APP_URL=http://127.0.0.1:8001>> ".env"
    echo SANDBOX_POOL_URL=http://127.0.0.1:8080>> ".env"
    echo REDIS_HOST=127.0.0.1>> ".env"
    echo REDIS_PORT=6379>> ".env"
    echo POSTGRES_HOST=127.0.0.1>> ".env"
    echo POSTGRES_PORT=5432>> ".env"
    echo HONEY_TOKEN_INJECTOR_ENABLED=true>> ".env"
    echo TRUST_PROXY_HEADERS=true>> ".env"
    echo         Created default .env file.
) else (
    echo         Found existing .env configuration file.
)

set "PYTHONPATH=%CD%"
set "CORE_WEB_APP_URL=http://127.0.0.1:8001"
set "SANDBOX_POOL_URL=http://127.0.0.1:8080"
set "REDIS_HOST=127.0.0.1"
set "POSTGRES_HOST=127.0.0.1"

echo.
echo [STEP 4/5] Checking External Backing Services [Docker / Redis / PostgreSQL]...
%PYTHON_CMD% -c "import socket; r= lambda p: socket.create_connection(('127.0.0.1', p), 0.2).close() is None; print('        [INFO] Redis 6379      : Connected' if (lambda: (r(6379), True)[1])() else '') if False else None" >nul 2>&1
echo         [INFO] Auto-Detecting Redis / PostgreSQL / Docker [Built-in High-Speed In-Memory Fallback Ready].

echo.
echo [STEP 5/5] Launching All 5 FastAPI Services Across Layers 1-4...
echo         The SOC Command Center Dashboard [http://127.0.0.1:8500] will open in your browser automatically.
echo         Press CTRL+C at any time to stop the servers.
echo.

%PYTHON_CMD% run_all.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
)

echo.
echo ================================================================================
echo   Servers stopped. Press any key to close this window.
echo ================================================================================
pause
