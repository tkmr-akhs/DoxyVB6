@ECHO off
SET BAT_PATH=%~dpnx0
FOR %%A IN ("%~dp0.") DO SET "BAT_DIR=%%~fA"
SET BAT_FILE=%~nx0

SET ARG_PATH=%~dpnx1
SET ARG_DIR=%~dp1.
SET ARG_FILE=%~nx1

SET TargetPathATTR=%~a1
SET TargetPathATTR=%TargetPathATTR:~0,1%
if "%~1"=="" (
  SET ARG_PATH=
  SET ARG_DIR=
  SET ARG_FILE=
) else (
  if /i "%TargetPathATTR%"=="d" (
    SET ARG_FILE=
    SET "ARG_DIR=%ARG_PATH%\."
  )
)
SET TargetPathATTR=

FOR %%A IN ("%ARG_DIR%") DO SET "ARG_DIR=%%~fA"

SET PS1FILE=%BAT_DIR%\build_document_main.ps1

ECHO Starting processing.
ECHO --------------------------------------------------------------------------
REM powershell -ExecutionPolicy bypass -NonInteractive -NoLogo -File "%~dp0\build_document_main.ps1" "%~dpnx1
powershell -ExecutionPolicy bypass -NoLogo -NonInteractive -File "%PS1FILE%" "%BAT_DIR%" "%BAT_FILE%" "%BAT_PATH%" "%ARG_DIR%" "%ARG_FILE%" "%ARG_PATH%"
ECHO --------------------------------------------------------------------------
ECHO Processing completed.
ECHO This window will close automatically in 1 minute. Processing has finished, so you may close the window or press CTRL+C.
TIMEOUT /T 60 /NOBREAK
