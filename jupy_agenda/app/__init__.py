import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail() # Initialize Mail

def create_app(config_class=None): # Added config_class argument
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True) # instance_relative_config=True

    if config_class:
        app.config.from_object(config_class)
        # Ensure instance folder path is set correctly if UPLOAD_FOLDER in TestConfig uses it
        # For 'sqlite:///:memory:', instance_path is less critical unless other features use it.
        if not os.path.exists(app.instance_path):
            try:
                os.makedirs(app.instance_path)
            except OSError as e:
                app.logger.warning(f"Could not create instance path for test config: {e}")
    else:
        # Default production/development configuration loaded from mapping and environment variables
        # Ensure instance folder exists for default config
        if not os.path.exists(app.instance_path):
            try:
                os.makedirs(app.instance_path)
            except OSError as e:
                # Log this error as it's for the main app operation
                app.logger.error(f"CRITICAL: Could not create instance path: {app.instance_path}, error: {e}")
                # Depending on the app, you might want to raise an exception or exit
        
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'your_default_secret_key_for_development'),
            # SQLALCHEMY_DATABASE_URI will be set below based on env var or default to project root
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            
            MAIL_SERVER=os.environ.get('MAIL_SERVER', 'localhost'), # Default for MailHog/console
            MAIL_PORT=int(os.environ.get('MAIL_PORT', 1025)),
            MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', '1', 't'],
            MAIL_USE_SSL=os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't'],
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
            MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@jupy.agenda'),
            
            UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads', 'learning_materials'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024,
            
            # Suppress email sending if FLASK_ENV is not 'production' AND no explicit MAIL_USERNAME is set.
            # This helps prevent accidental email sending in dev/test if MAIL_SERVER is misconfigured.
            MAIL_SUPPRESS_SEND=(os.environ.get('FLASK_ENV', 'development').lower() != 'production' and \
                               not os.environ.get('MAIL_USERNAME'))
        )
        
        # Set default SQLALCHEMY_DATABASE_URI to project_root/database/agenda.db if not overridden by env var
        default_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'agenda.db'))
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', f'sqlite:///{default_db_path}')
        
        # Ensure directory for SQLite file exists if it's being used
        if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:///'):
            db_file_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            db_dir = os.path.dirname(db_file_path)
            if not os.path.exists(db_dir):
                try:
                    os.makedirs(db_dir)
                except OSError as e:
                    app.logger.error(f"Error creating database directory {db_dir}: {e}")
    # If config_class is provided (e.g. TestConfig), SQLALCHEMY_DATABASE_URI is already set from there.

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app) # Initialize Mail with app

    # Flask-Login configuration
    login_manager.login_view = 'auth.login'  # The route name for the login page (blueprint.route_function)
    login_manager.login_message_category = 'info' # Flash message category

    # User loader function for Flask-Login
    # This callback is used to reload the user object from the user ID stored in the session.
    # It should take the str ID of a user, and return the corresponding user object,
    # or None if the ID is not valid.
    @login_manager.user_loader
    def load_user(user_id):
        # Import User model here to avoid circular imports
        from .models import User
        return User.query.get(int(user_id))

    # Register Blueprints
    from .auth_routes import auth_bp
    from .main_routes import main_bp
    from .calendar_routes import calendar_bp
    from .todo_routes import todo_bp
    from .location_routes import location_bp
    from .diagram_routes import diagram_bp
    from .code_snippet_routes import code_snippet_bp
    from .material_routes import material_bp
    from .note_routes import note_bp
    from .stats_routes import stats_bp # Import the new stats blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/') 
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(todo_bp, url_prefix='/todo')
    app.register_blueprint(location_bp, url_prefix='/locations')
    app.register_blueprint(diagram_bp, url_prefix='/diagrams')
    app.register_blueprint(code_snippet_bp, url_prefix='/code')
    app.register_blueprint(material_bp, url_prefix='/materials')
    app.register_blueprint(note_bp, url_prefix='/notes')
    app.register_blueprint(stats_bp, url_prefix='/statistics') # Register stats blueprint

    # Create database tables if they don't exist
    # This is a simple way to ensure tables are created.
    # For more complex scenarios, Flask-Migrate is recommended.
    with app.app_context():
        # Ensure all models are imported before calling db.create_all()
        # This might require importing models from various blueprints if not already done
        from . import models # Ensure all models in models.py are loaded
        
        db.create_all()
        
        # Create upload folder if it doesn't exist (app.config['UPLOAD_FOLDER'] should be set by now)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            try:
                os.makedirs(app.config['UPLOAD_FOLDER'])
                # current_app.logger.info(f"Upload folder created at: {app.config['UPLOAD_FOLDER']}")
            except OSError as e:
                current_app.logger.error(f"Error creating upload folder {app.config['UPLOAD_FOLDER']}: {e}")
        
        # The db_path variable from the original code might be confusing here as SQLALCHEMY_DATABASE_URI is now set.
        # The directory for the SQLite file (if not in-memory) should be ensured by the config logic above.
        # For the default case, it's project_root/database/. For tests, it's in-memory or TestConfig defined.

    return app
