# Jupy Project - Jupy Agenda Application

## Overview

This repository contains the Jupy Agenda Flask application, a web-based agenda to manage tasks, events, and reminders.

## Prerequisites

*   **Python 3:** Version 3.7+ is recommended. You can download it from [python.org](https://www.python.org/).
*   **pip:** Usually included with Python. This is Python's package installer.
*   **Git:** For cloning the repository. You can download it from [git-scm.com](https://git-scm.com/).
*   **(For Linux users):** If you encounter issues creating a virtual environment (e.g., `python3 -m venv` fails), you might need to install the `python3-venv` package.
    *   On Debian/Ubuntu: `sudo apt-get install python3-venv`
    *   On Fedora: `sudo dnf install python3-venv`

## Getting Started / Installation

1.  **Clone the repository:**
    Open your terminal or command prompt, navigate to where you want to place the project, and run:
    ```bash
    git clone https://github.com/your-username/jupy-agenda.git # Replace with the actual repository URL
    cd jupy-agenda # Or your project's root directory name
    ```

2.  **Recommended Setup (using provided scripts):**
    These scripts automate the setup process, including virtual environment creation, dependency installation, and initial configuration. They are located in the project root directory.

    *   **On Linux or macOS:**
        Navigate to the project root directory in your terminal and run:
        ```bash
        bash setup_and_run_linux.sh
        ```

    *   **On Windows:**
        Navigate to the project root directory in your command prompt or PowerShell and run:
        ```batch
        setup_and_run_windows.bat
        ```

    **These scripts will:**
    *   Check for a valid Python 3 installation.
    *   Set up a Python virtual environment in a directory named `venv/` within the project root.
    *   Activate the virtual environment for the script session.
    *   Install all necessary Python packages listed in `jupy_agenda/requirements.txt`.
    *   Copy the environment variable template `jupy_agenda/.env.example` to `jupy_agenda/.env` if `.env` does not already exist.
        *   **Important:** You should review and customize `jupy_agenda/.env` with your specific settings (e.g., `SECRET_KEY`, email server details if you plan to use email notifications, database URI if not using the default SQLite).
    *   Offer to start the development server.

## Running the Development Server (if not started by script)

If you chose not to start the server via the setup script, or if you need to restart it later:

1.  **Activate the virtual environment:**
    Ensure you are in the project root directory.
    *   **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```
    *   **Windows:**
        ```batch
        venv\Scripts\activate.bat
        ```
    Your terminal prompt should change to indicate that the virtual environment is active (e.g., `(venv) your-prompt$`).

2.  **Run the application:**
    Ensure you are in the project root directory.
    ```bash
    python jupy_agenda/run.py
    ```

3.  **Access the application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Running Tests

To run the automated tests for the application:

1.  **Activate the virtual environment** (if not already active):
    Ensure you are in the project root directory.
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate.bat`

2.  **Run the test suite:**
    Ensure you are in the project root directory.
    ```bash
    python jupy_agenda/run.py test
    ```
    This command will discover and execute tests located in the `jupy_agenda/tests/` directory.

## Configuration

*   The application is configured primarily via **environment variables**.
*   A template file, `jupy_agenda/.env.example`, is provided with common variables. The setup scripts (`setup_and_run_linux.sh` or `setup_and_run_windows.bat`) will copy this to `jupy_agenda/.env` if `.env` doesn't already exist.
*   **You should review and update `jupy_agenda/.env`** with your specific settings, especially for:
    *   `SECRET_KEY`: A strong, unique secret for session security.
    *   `SQLALCHEMY_DATABASE_URI`: Defaults to SQLite. Change if you want to use PostgreSQL or another database.
    *   `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, etc.: If you want to enable email notifications for reminders.
*   The `jupy_agenda/run.py` script automatically loads variables from a `.env` file located at `jupy_agenda/.env` at startup using the `python-dotenv` library.

## Production Notes

For deploying the application in a production environment:

1.  **Set Flask Environment:**
    In your `jupy_agenda/.env` file, set:
    ```
    FLASK_ENV=production
    ```
    And ensure `DEBUG=False` (or remove the `DEBUG` variable as it defaults to `False` when `FLASK_ENV` is `production`).

2.  **Use a Production-Ready WSGI Server:**
    The Flask development server (`app.run()`) is not suitable for production. Use a dedicated WSGI server like Gunicorn (for Linux) or Waitress (for Windows/cross-platform).

    *   **Gunicorn (Linux/macOS):**
        First, install Gunicorn in your virtual environment:
        ```bash
        pip install gunicorn
        ```
        Then run the application (from the project root directory):
        ```bash
        gunicorn --workers 4 --bind 0.0.0.0:5000 "jupy_agenda.app:create_app()"
        ```
        Adjust the number of workers (`--workers`) and the bind address (`--bind`) as needed.

    *   **Waitress (Windows & other platforms):**
        First, install Waitress in your virtual environment:
        ```bash
        pip install waitress
        ```
        Then run the application (from the project root directory):
        ```bash
        waitress-serve --listen=0.0.0.0:5000 "jupy_agenda.app:create_app()"
        ```
        Adjust the listen address (`--listen`) as needed.

3.  **Database:**
    Consider using a more robust database like PostgreSQL in production. Update `SQLALCHEMY_DATABASE_URI` in your `.env` file accordingly and ensure the necessary database drivers (e.g., `psycopg2-binary`) are installed.

4.  **Secret Key:**
    Ensure `SECRET_KEY` in your `.env` file is a long, random, and unique string. Do not use the default example key.

## Jupy Agenda Application Details

For detailed information about the Jupy Agenda application itself, its features, API (if any), advanced configuration specific to the agenda functionalities, and contribution guidelines, please see the dedicated README located at:
[`jupy_agenda/README.md`](jupy_agenda/README.md)
