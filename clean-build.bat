@echo off
rem Batch scripting reference:
rem http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/batch.mspx

set DIR_NAMES=bin obj x86 x64 Debug Release Build ipch

echo Removing user files:
erase /s /q /ah *.suo  2> nul
erase /s /q     *.user 2> nul

echo Removing intellisense files:
erase /s /q *.ncb *.sdf 2> nul

echo Removing backup files:
erase /s /q *~ 2> nul

echo Removing build directories:
for /f "usebackq delims=" %%d in (`dir /ad /b /s ^| sort /r`) do (
	for %%n in (%DIR_NAMES%) do (
		if /i "%%~nd" == "%%n" (
			rd /s /q "%%d"
			echo Deleted directory - %%d
		)
	)
)

pause
