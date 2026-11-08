@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
if not exist ".env" (
  if exist ".env.example" copy /y ".env.example" ".env" >nul
)
echo.
echo ================== FONOAPP ==================
echo Instalando las dependencias necesarias...
if not exist ".venv\Scripts\python.exe" (
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -m venv .venv
  )
  if errorlevel 1 goto error
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
findstr /c:"MONGODB_URI=mongodb://127.0.0.1:27017" ".env" >nul 2>&1
if not errorlevel 1 (
  echo.
  echo AVISO: Este .env apunta a MongoDB LOCAL.
  echo Si usas Atlas, conserva y copia el .env del proyecto anterior.
  echo Sin la URI real de Atlas no sera posible iniciar sesion.
  echo.
)
echo Abre en el navegador: http://127.0.0.1:8000
".venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if errorlevel 1 goto error
goto fin
:error
echo.
echo No se pudo iniciar FonoApp. Revisa las lineas anteriores.
pause
:fin
endlocal
