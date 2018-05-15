@echo off

if exist "%PROGRAMFILES%\Git\git-cmd.exe" (
	"%PROGRAMFILES%\Git\git-cmd.exe" "py -3 "%~dp0\repos.py" %* & exit"
)
