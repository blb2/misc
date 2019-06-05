@echo off

if exist "%PROGRAMFILES%\Git\git-cmd.exe" (
	"%PROGRAMFILES%\Git\git-cmd.exe" --command=usr\bin\bash.exe -l -c 'py -3 "%~dp0\repos.py" %*'
)
