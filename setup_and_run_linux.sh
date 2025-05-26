#!/bin/bash

# Welcome message
echo "Welcome to the Jupy Agenda Setup Script for Linux/macOS!"
echo "-------------------------------------------------------"

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi
echo "Python 3 found: $(python3 --version)"

# Check for pip
if ! python3 -m pip --version &> /dev/null
then
    echo "Error: pip for Python 3 is not available."
    echo "Please try running: python3 -m ensurepip --upgrade"
    echo "Or ensure Python 3 was installed with pip support."
    exit 1
fi
echo "pip found: $(python3 -m pip --version | head -n 1)"

# Define virtual environment directory
VENV_DIR="venv"
SCRIPT_DIR_PARENT=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
VENV_PATH="$SCRIPT_DIR_PARENT/$VENV_DIR" # Absolute path for clarity in messages

echo "Virtual environment will be set up in: $VENV_PATH"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    if ! python3 -m venv "$VENV_PATH"; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"
echo "Virtual environment activated for this script session."
echo "If you want to use this virtual environment in your terminal later, please run: source $VENV_DIR/bin/activate"
echo "(Assuming you are in the project root directory: $SCRIPT_DIR_PARENT)"


# Upgrade pip
echo "Upgrading pip..."
if ! pip install --upgrade pip; then
    echo "Error: Failed to upgrade pip."
    # Attempt to deactivate venv before exiting, though script termination will effectively do this.
    deactivate &> /dev/null
    exit 1
fi
echo "pip upgraded successfully."

# Install dependencies
REQUIREMENTS_FILE="jupy_agenda/requirements.txt"
echo "Installing dependencies from $REQUIREMENTS_FILE..."
if [ ! -f "$SCRIPT_DIR_PARENT/$REQUIREMENTS_FILE" ]; then
    echo "Error: $REQUIREMENTS_FILE not found in $SCRIPT_DIR_PARENT/jupy_agenda/."
    deactivate &> /dev/null
    exit 1
fi

if ! pip install -r "$SCRIPT_DIR_PARENT/$REQUIREMENTS_FILE"; then
    echo "Error: Failed to install dependencies from $REQUIREMENTS_FILE."
    deactivate &> /dev/null
    exit 1
fi
echo "Dependencies installed successfully."

# Check for .env file
ENV_FILE_EXAMPLE_PATH="jupy_agenda/.env.example"
ENV_FILE_PATH="jupy_agenda/.env"

if [ ! -f "$SCRIPT_DIR_PARENT/$ENV_FILE_PATH" ]; then
    echo ".env file not found."
    if [ -f "$SCRIPT_DIR_PARENT/$ENV_FILE_EXAMPLE_PATH" ]; then
        echo "Copying $ENV_FILE_EXAMPLE_PATH to $ENV_FILE_PATH..."
        if ! cp "$SCRIPT_DIR_PARENT/$ENV_FILE_EXAMPLE_PATH" "$SCRIPT_DIR_PARENT/$ENV_FILE_PATH"; then
            echo "Error: Failed to copy .env.example to .env."
            # No need to exit, but inform user
        else
            echo "Successfully copied .env.example to .env."
            echo "IMPORTANT: Please review and edit $SCRIPT_DIR_PARENT/$ENV_FILE_PATH with your specific configurations."
        fi
    else
        echo "Warning: $ENV_FILE_EXAMPLE_PATH not found. Cannot create .env file."
        echo "Please ensure you have a .env file or .env.example in the jupy_agenda directory."
    fi
else
    echo ".env file already exists at $SCRIPT_DIR_PARENT/$ENV_FILE_PATH. No action taken."
fi

echo "-------------------------------------------------------"
echo "Setup complete!"
echo "-------------------------------------------------------"

# Ask to run development server
read -p "Do you want to run the development server now? (y/n): " choice
case "$choice" in
  y|Y )
    echo "Starting development server..."
    if ! python "$SCRIPT_DIR_PARENT/jupy_agenda/run.py"; then
        echo "Error: Failed to start the development server."
        echo "Make sure you are in the virtual environment. Try running these commands manually:"
        echo "1. cd $SCRIPT_DIR_PARENT"
        echo "2. source $VENV_DIR/bin/activate"
        echo "3. python jupy_agenda/run.py"
    fi
    ;;
  n|N )
    echo "You can run the development server later by navigating to the project root directory ($SCRIPT_DIR_PARENT) and running:"
    echo "1. source $VENV_DIR/bin/activate"
    echo "2. python jupy_agenda/run.py"
    ;;
  * )
    echo "Invalid choice. Please run the server manually if needed:"
    echo "1. cd $SCRIPT_DIR_PARENT"
    echo "2. source $VENV_DIR/bin/activate"
    echo "3. python jupy_agenda/run.py"
    ;;
esac

echo "Exiting setup script."
# Deactivation will happen automatically when the script exits if it was sourced.
# If the script was run directly, the 'source' command affects only the script's subshell.
# The message about manual activation for the user's terminal is key.
