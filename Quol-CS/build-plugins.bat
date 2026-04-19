@echo off
:: Wrapper to run build-plugins.ps1 from Windows Explorer or cmd
:: Usage: build-plugins.bat [Debug|Release]  (default: Debug)

set CONFIG=%~1
if "%CONFIG%"=="" set CONFIG=Debug

powershell -ExecutionPolicy Bypass -File "%~dp0build-plugins.ps1" -Configuration %CONFIG%
pause
