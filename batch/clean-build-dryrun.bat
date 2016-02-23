@echo off
rem Batch scripting reference:
rem http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/batch.mspx

set PAUSE=%~1
set DIR_NAMES=bin obj ipch

echo User files to remove:
dir /s /b /ah *.suo  2> nul
dir /s /b     *.suo  2> nul
dir /s /b     *.user 2> nul

echo Intellisense files to remove:
dir /s /b *.ncb *.sdf 2> nul
dir /s /b *.aps       2> nul

echo Backup files to remove:
dir /s /b *~ 2> nul

echo Build directories to remove:
for /f "usebackq delims=" %%d in (`dir /ad /b /s ^| sort /r`) do (
	for %%n in (%DIR_NAMES%) do (
		if /i "%%~nxd" == "%%n" (
			echo %%d
		)
	)
)

if "%PAUSE%"=="" pause
