@echo off
:: Wrapper to run build-plugins.ps1 from Windows Explorer or cmd
:: Usage: build-plugins.bat [Debug|Release] [PluginFolderName]
:: Examples:
::   build-plugins.bat
::   build-plugins.bat PluginExample
::   build-plugins.bat Debug
::   build-plugins.bat Debug PluginExample

set CONFIG=Debug
set PLUGIN=

if /I "%~1"=="Debug" (
	set CONFIG=%~1
	set PLUGIN=%~2
) else if /I "%~1"=="Release" (
	set CONFIG=%~1
	set PLUGIN=%~2
) else (
	set PLUGIN=%~1
)

powershell -ExecutionPolicy Bypass -File "%~dp0build-plugins.ps1" -Configuration %CONFIG% -PluginName "%PLUGIN%"
pause
