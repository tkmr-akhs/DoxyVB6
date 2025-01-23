REM deactivate

RMDIR /s /q build_env\.env
RMDIR /s /q build_env\src

COPY /y pyproject.toml build_env\
COPY /y poetry.lock build_env\
COPY /y README.md build_env\
XCOPY /e /y src build_env\src\

CD build_env

poetry install --only main

CD ..

RMDIR /s /q dist
MKDIR dist

REM CALL build_env\.venv\Scripts\activate.bat & pyinstaller src\main.py --name DoxyVB6 --onefile --clean & deactivate

CALL build_env\.venv\Scripts\activate.bat
pyinstaller src\main.py --name DoxyVB6 --onefile --clean
CALL build_env\.venv\Scripts\deactivate.bat

RMDIR /s /q build
DEL /q build_env\pyproject.toml
DEL /q build_env\poetry.lock
DEL /q build_env\README.md
RMDIR /s /q build_env\src
RMDIR /s /q build_env\.venv