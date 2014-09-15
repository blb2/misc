@echo off
rem Batch scripting reference:
rem http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/batch.mspx

set SZ=%PROGRAMFILES%\7-Zip\7z.exe
set SRC=%APPDATA%\.minecraft\saves
set DST=%USERPROFILE%\Desktop\Minecraft Backups
set DSTNAME=Backup
set DSTEXT=7z

set /a N=0
:get_unique_name
set /a N+=1
if exist "%DST%\%DSTNAME%%N%.%DSTEXT%" goto :get_unique_name

if exist "%SZ%" (
	if exist "%SRC%" (
		if not exist "%DST%" mkdir "%DST%"
		"%SZ%" a -t7z -mx=9 -mmt=on "%DST%\%DSTNAME%%N%.%DSTEXT%" "%SRC%"
	) else (
		echo Minecraft save location not found:
		echo %SRC%
	)
) else (
	echo 7-zip not found:
	echo %SZ%
)

pause
