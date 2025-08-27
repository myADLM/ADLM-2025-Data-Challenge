@echo off
setlocal
pushd "%~dp0"



start "" /D "%CD%" powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File ".\run_windows.ps1"

popd
endlocal
exit /b
