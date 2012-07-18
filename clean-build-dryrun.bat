@echo off
rem Batch scripting reference:
rem http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/batch.mspx

set DIR_NAMES=bin obj x86 x64 Debug Release Build

echo User files to remove:
dir /s /b /ah *.suo  2> nul
dir /s /b     *.user 2> nul

echo Intellisense files to remove:
dir /s /b *.ncb *.sdf 2> nul

echo Backup files to remove:
dir /s /b *~ 2> nul

echo Build directories to remove:
for /f "usebackq delims=" %%d in (`dir /ad /b /s ^| sort /r`) do (
	setlocal enabledelayedexpansion

	set DIR_NAME=%%~nd
	for %%n in (%DIR_NAMES%) do (
		if /i "!DIR_NAME!" == "%%n" (
			echo %%d
		)
	)

	endlocal
)

pause
