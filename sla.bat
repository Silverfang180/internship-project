@echo off
set PYTHONPATH=.

set COMMAND=%1
shift

if "%COMMAND%"=="clean" (
    .\.venv\Scripts\python -m src.clean %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b
)
if "%COMMAND%"=="test" (
    .\.venv\Scripts\python -m pytest -q %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b
)
if "%COMMAND%"=="report" (
    if "%1"=="" (
        .\.venv\Scripts\python -m src.report --interactive
    ) else (
        .\.venv\Scripts\python -m src.report %1 %2 %3 %4 %5 %6 %7 %8 %9
    )
    exit /b
)
if "%COMMAND%"=="validate" (
    .\.venv\Scripts\python -m src.validate %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b
)
if "%COMMAND%"=="score" (
    .\.venv\Scripts\python -m src.score_validation %1 %2 %3 %4 %5 %6 %7 %8 %9
    exit /b
)

echo SLA Intelligence CLI Shortcuts
echo ------------------------------
echo sla report    - Run the interactive manager report (default)
echo sla clean     - Run the data cleaning pipeline
echo sla test      - Run the pytest suite
echo sla validate  - Generate validation benchmark
echo sla score     - Score validation answers
