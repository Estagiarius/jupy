@echo off
setlocal

REM Welcome message
echo Welcome to the Jupy Agenda Setup Script for Windows!
echo ----------------------------------------------------

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not added to PATH.
    echo Please install Python from python.org and ensure it's added to your PATH.
    goto :eof
)
echo Python found.

REM Define virtual environment directory
SET VENV_DIR=venv
SET SCRIPT_DIR=%~dp0
SET VENV_PATH=%SCRIPT_DIR%%VENV_DIR%

echo Virtual environment will be set up in: %VENV_PATH%

REM Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        goto :eof
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_PATH%\Scripts\activate.bat"
echo Virtual environment activated for this script session.
echo If you want to use this virtual environment in your terminal later, please run:
echo %VENV_DIR%\Scripts\activate.bat
echo (Assuming you are in the project root directory: %SCRIPT_DIR%)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Error: Failed to upgrade pip.
    goto :deactivate_and_exit
)
echo pip upgraded successfully.

REM Install dependencies
SET REQUIREMENTS_FILE=jupy_agenda\requirements.txt
echo Installing dependencies from %REQUIREMENTS_FILE%...
if not exist "%SCRIPT_DIR%%REQUIREMENTS_FILE%" (
    echo Error: %REQUIREMENTS_FILE% not found in %SCRIPT_DIR%jupy_agenda\
    goto :deactivate_and_exit
)

python -m pip install -r "%SCRIPT_DIR%%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo Error: Failed to install dependencies from %REQUIREMENTS_FILE%.
    goto :deactivate_and_exit
)
echo Dependencies installed successfully.

REM Check for .env file
SET ENV_FILE_EXAMPLE_PATH=jupy_agenda\.env.example
SET ENV_FILE_PATH=jupy_agenda\.env

if not exist "%SCRIPT_DIR%%ENV_FILE_PATH%" (
    echo .env file not found.
    if exist "%SCRIPT_DIR%%ENV_FILE_EXAMPLE_PATH%" (
        echo Copying %ENV_FILE_EXAMPLE_PATH% to %ENV_FILE_PATH%...
        copy "%SCRIPT_DIR%%ENV_FILE_EXAMPLE_PATH%" "%SCRIPT_DIR%%ENV_FILE_PATH%" /Y >nul
        if errorlevel 1 (
            echo Error: Failed to copy .env.example to .env.
            REM No need to exit, but inform user
        ) else (
            echo Successfully copied .env.example to .env.
            echo IMPORTANT: Please review and edit %SCRIPT_DIR%%ENV_FILE_PATH% with your specific configurations.
        )
    ) else (
        echo Warning: %ENV_FILE_EXAMPLE_PATH% not found. Cannot create .env file.
        echo Please ensure you have a .env file or .env.example in the jupy_agenda directory.
    )
) else (
    echo .env file already exists at %SCRIPT_DIR%%ENV_FILE_PATH%. No action taken.
)

echo ----------------------------------------------------
echo Setup complete!
echo ----------------------------------------------------

REM Ask to run development server
:ask_run_server
set /p choice="Do you want to run the development server now? (y/n): "
if /i "%choice%"=="y" goto :run_server
if /i "%choice%"=="n" goto :no_run_server
echo Invalid choice. Please enter 'y' or 'n'.
goto :ask_run_server

:run_server
echo Starting development server...
python "%SCRIPT_DIR%jupy_agenda\run.py"
if errorlevel 1 (
    echo Error: Failed to start the development server.
    echo Make sure you are in the virtual environment. Try running these commands manually:
    echo 1. cd %SCRIPT_DIR%
    echo 2. %VENV_DIR%\Scripts\activate.bat
    echo 3. python jupy_agenda\run.py
)
goto :end_script

:no_run_server
echo You can run the development server later by navigating to the project root directory (%SCRIPT_DIR%) and running:
echo 1. %VENV_DIR%\Scripts\activate.bat
echo 2. python jupy_agenda\run.py
goto :end_script

:deactivate_and_exit
echo An error occurred. Deactivating virtual environment if active.
call deactivate >nul 2>&1
goto :eof

:end_script
echo Exiting setup script.
REM Deactivation will happen if 'deactivate.bat' is callable and venv was active.
call deactivate >nul 2>&1
endlocal
