@echo off
REM Wizard's Castle - lanzador Windows.
REM Encuentra Python (py -3 > python > python3) y ejecuta run.py.
REM Doble-clic en este archivo desde el Explorador para arrancar el juego.

setlocal
cd /d "%~dp0"

REM 1) Launcher oficial de Python en Windows (py.exe)
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 run.py %*
    goto :end
)

REM 2) python.exe en PATH
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python run.py %*
    goto :end
)

REM 3) python3.exe (algunos instaladores lo crean)
where python3 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python3 run.py %*
    goto :end
)

echo.
echo [ERROR] No se encontro Python instalado.
echo.
echo Descarga Python 3.11 o superior desde:
echo     https://www.python.org/downloads/
echo.
echo Importante: al instalar, marca la casilla "Add Python to PATH".
echo.
pause

:end
endlocal
