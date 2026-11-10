@echo off
setlocal
cd /d "%~dp0"

rem Установка зависимости (тихо, если ещё не стоит)
python -m pip install -q pyyaml
if errorlevel 1 (
    echo Ошибка: не удалось установить pyyaml
    exit /b 1
)

rem Запуск: run.bat [путь_к_конфигу]
set CONFIG=%1
if "%CONFIG%"=="" set CONFIG=config.yaml

python -m src.main -c "%CONFIG%"
exit /b %errorlevel%