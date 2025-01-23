@ECHO OFF

powershell -ExecutionPolicy bypass -NonInteractive -NoLogo -File "%~dp0\build_document_main.ps1" "%~dpnx1

ECHO This window will automatically close in one minute. The process has already finished, so there is no problem if you close the window or press CTRL+C to exit.
TIMEOUT /T 60 /NOBREAK