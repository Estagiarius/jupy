# Jupy Agenda

Jupy Agenda is a comprehensive personal management application built with Flask. It helps users organize their schedules, tasks, notes, and more.

## Features

*   User Authentication (Registration, Login, Logout)
*   Calendar with Event Management
*   To-Do List with Task Management (Priority, Due Dates, Status)
*   Location Storage
*   Diagram Notes (Text-based diagrams)
*   Code Snippets Storage
*   Learning Materials Manager (File Uploads/Downloads)
*   Quick Notes with Categorization and Search
*   Email Reminders for Events and Tasks
*   Statistics and Reports on user activity

## Project Structure

```
jupy_agenda/
├── app/                     # Main application package
│   ├── __init__.py          # Application factory (create_app)
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── services/            # Business logic (e.g., statistics, notifications)
│   ├── static/              # Static files (CSS, JS, images)
│   ├── templates/           # HTML templates (organized by feature)
│   │   ├── auth/
│   │   ├── calendar/
│   │   ├── code_snippets/
│   │   ├── diagrams/
│   │   ├── email/
│   │   ├── locations/
│   │   ├── materials/
│   │   ├── notes/
│   │   ├── stats/
│   │   └── base.html        # Base template
│   ├── auth_routes.py       # Authentication blueprints
│   ├── calendar_routes.py   # Calendar blueprints
│   └── ... (other feature-specific route files)
├── database/                # Default location for SQLite database file (if used locally)
├── instance/                # Instance folder (for uploads, instance-specific config)
│   ├── uploads/             # User uploaded files
│   └── .gitignore           # Ignores instance content
├── tests/                   # Unit and functional tests
│   ├── __init__.py
│   ├── base_test.py
│   ├── test_config.py
│   ├── functional/
│   └── unit/
├── .gitignore               # Main gitignore file
├── Procfile                 # For Heroku/Gunicorn
├── README.md                # This file
├── requirements.txt         # Python dependencies
└── run.py                   # Application runner, CLI commands (tests, reminders)
```

## Local Development Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd jupy_agenda_project_root # The directory containing the jupy_agenda folder
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r jupy_agenda/requirements.txt
    ```

4.  **Set up Environment Variables (Optional for basic local running with defaults):**
    Create a `.env` file in the `jupy_agenda` directory (or set them in your shell):
    ```env
    # In jupy_agenda/.env
    # FLASK_APP="run.py" # Not strictly needed if running run.py directly
    FLASK_ENV="development" # Enables debug mode
    SECRET_KEY="a_very_secret_key_for_development_only" 
    # SQLALCHEMY_DATABASE_URI="sqlite:///database/agenda.db" # Default is already this
    # MAIL_SERVER="localhost" # For MailHog or local SMTP
    # MAIL_PORT=1025
    # MAIL_USERNAME=""
    # MAIL_PASSWORD=""
    # MAIL_DEFAULT_SENDER="dev-noreply@jupy.agenda"
    ```
    If using a `.env` file, ensure `python-dotenv` is installed and `run.py` loads it (currently not implemented in `run.py`, so export them or set in IDE). For simplicity, the app uses defaults if env vars are not set.

5.  **Initialize the database:**
    The database and upload folders are typically created automatically when the application first runs via `create_app()`.

6.  **Run the development server:**
    Navigate into the `jupy_agenda` directory if you are in the project root.
    ```bash
    # Assuming you are in the 'jupy_agenda' directory where run.py is located
    python run.py 
    ```
    Or, if `FLASK_APP` is set and you are in the directory containing `jupy_agenda` folder:
    ```bash
    # flask run # This requires FLASK_APP to be set to jupy_agenda.run or similar.
    ```
    The application should be available at `http://127.0.0.1:5000/`.

7.  **Run Tests:**
    From the `jupy_agenda` directory:
    ```bash
    python run.py test
    ```

8.  **Send Reminders (Manual Trigger):**
    From the `jupy_agenda` directory:
    ```bash
    flask send-reminders 
    # This requires FLASK_APP=run.py to be set in the environment for the flask CLI to find the command.
    # Alternatively, ensure your current directory is `jupy_agenda` when running this.
    ```

## Deployment (Example with Gunicorn)

This application is configured to be deployed using a WSGI server like Gunicorn.

1.  **Install Dependencies:**
    Ensure all dependencies, including Gunicorn, are installed:
    ```bash
    pip install -r requirements.txt 
    # (requirements.txt is inside the jupy_agenda directory)
    ```

2.  **Set Environment Variables:**
    For a production environment, the following environment variables **must** be set:
    *   `FLASK_ENV="production"`: Disables debug mode and other development features.
    *   `SECRET_KEY`: A strong, unique, and secret key. **Do not use the development default.**
    *   `SQLALCHEMY_DATABASE_URI`: The connection string for your production database (e.g., PostgreSQL, MySQL).
        Example for PostgreSQL: `postgresql://user:password@host:port/database`
    *   `MAIL_SERVER`: Your SMTP server address.
    *   `MAIL_PORT`: Your SMTP server port (e.g., 587 for TLS, 465 for SSL).
    *   `MAIL_USE_TLS` / `MAIL_USE_SSL`: Set one to `true` depending on your SMTP server's requirements.
    *   `MAIL_USERNAME`: Your SMTP username.
    *   `MAIL_PASSWORD`: Your SMTP password.
    *   `MAIL_DEFAULT_SENDER`: The default "from" address for emails sent by the application.
    *   `UPLOAD_FOLDER`: (Optional, defaults to `instance/uploads/learning_materials`) Define if you need a custom path. Ensure this path is writable by the application server process.

3.  **Run with Gunicorn:**
    From the directory containing the `jupy_agenda` package (i.e., the project root):
    ```bash
    gunicorn "jupy_agenda.app:create_app()"
    ```
    You can customize Gunicorn settings (workers, host, port, etc.):
    ```bash
    gunicorn --workers 4 --bind 0.0.0.0:8000 "jupy_agenda.app:create_app()"
    ```

4.  **Reminder Sending Task:**
    The `flask send-reminders` command needs to be scheduled to run periodically (e.g., using cron, systemd timers, or a scheduler service provided by your hosting platform).
    Example cron job (runs every 5 minutes):
    ```cron
    */5 * * * * /path/to/your/project/venv/bin/flask -A /path/to/your/project/jupy_agenda/run.py send-reminders >> /var/log/jupy_agenda_reminders.log 2>&1
    ```
    Adjust paths and `FLASK_APP` (`-A` flag) as necessary for your environment.

## Contributing
Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## License
This project is licensed under the MIT License. (To be added formally)
