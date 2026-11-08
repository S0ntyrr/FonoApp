Set-Location $PSScriptRoot
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path .venv\Scripts\python.exe)) { py -3 -m venv .venv }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Error instalando dependencias' }
if (Select-String -Path .env -SimpleMatch 'MONGODB_URI=mongodb://127.0.0.1:27017' -Quiet) {
    Write-Warning 'Este .env usa MongoDB local. Si trabajas con Atlas, copia el .env que ya funciona en tu proyecto anterior.'
}
Write-Host 'Abre http://127.0.0.1:8000 en tu navegador'
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
