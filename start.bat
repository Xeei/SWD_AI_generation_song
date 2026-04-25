@echo off
set BASE_DIR=%cd%

echo =========================================
echo 🚀 Launching production environment...
echo =========================================

echo 📦 Starting Frontend...
start "Frontend" cmd /c "cd %BASE_DIR%\frontend && npm run start"

timeout /t 1 /nobreak >nul

echo 🐍 Starting Backend...
if exist "%BASE_DIR%\.venv\Scripts\activate.bat" (
    call "%BASE_DIR%\.venv\Scripts\activate.bat"
)
python "%BASE_DIR%\manage.py" makemigrations
python "%BASE_DIR%\manage.py" migrate --run-syncdb
python "%BASE_DIR%\manage.py" runserver 0.0.0.0:8000
