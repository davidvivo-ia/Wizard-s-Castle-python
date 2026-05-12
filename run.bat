@echo off
REM Wizard's Castle — lanzador Windows.
REM Usa `uv` si está disponible (recomendado); si no, cae a `python run.py`.

setlocal
cd /d "%~dp0"

where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    uv run wizards-castle %*
    goto :end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py %*
    goto :end
)

echo Necesitas Python 3.13+ instalado.
echo Descárgalo en https://www.python.org/downloads/
pause

:end
endlocal
