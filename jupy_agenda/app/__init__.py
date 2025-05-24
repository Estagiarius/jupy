import os
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail() # Initialize Mail

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Configuration
    # In a real app, use environment variables or a config file.
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key_for_development')
    
    # Mail configuration - for development, emails can be printed to console or use a tool like MailHog
    # For production, set these environment variables appropriately.
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost') # e.g., 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 1025))     # e.g., 587 for TLS, 465 for SSL
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'false').lower() in ['true', '1', 't']
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')             # e.g., your-email@example.com
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')             # e.g., your-email-password
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@jupy.agenda')

    # Upload folder configuration
    # Using os.path.abspath to ensure it's an absolute path
    # app.instance_path is the 'instance' folder at the root of the project
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads', 'learning_materials')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit for uploads

    # For development, to print emails to console instead of sending:
    # Set MAIL_SUPPRESS_SEND to True (or leave MAIL_SERVER as localhost and port 1025 if using MailHog)
    # If MAIL_SERVER is 'localhost' and MAIL_PORT is 1025, it's typically for MailHog.
    # If you want to truly suppress sending and not even try to connect to a mail server:
    app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('FLASK_ENV') == 'development' and not app.config['MAIL_USERNAME']
    # app.config['MAIL_DEBUG'] = True # Default is app.debug, which is True in dev from run.py

    # Construct the absolute path for the database file
    # The database file will be 'jupy_agenda/database/agenda.db'
    # __file__ is jupy_agenda/app/__init__.py
    # os.path.dirname(__file__) is jupy_agenda/app
    # os.path.join(os.path.dirname(__file__), '..', 'database', 'agenda.db') navigates up and then to database/
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'agenda.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(db_path)}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    from .material_routes import material_bp # Import the new material blueprint
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/') 
    app.register_blueprint(calendar_bp, url_prefix='/calendar')
    app.register_blueprint(todo_bp, url_prefix='/todo')
    app.register_blueprint(location_bp, url_prefix='/locations')
    app.register_blueprint(diagram_bp, url_prefix='/diagrams')
    app.register_blueprint(code_snippet_bp, url_prefix='/code')
    app.register_blueprint(material_bp, url_prefix='/materials') # Register material blueprint

    # Create database tables if they don't exist
    # This is a simple way to ensure tables are created.
    # For more complex scenarios, Flask-Migrate is recommended.
    with app.app_context():
        # Ensure all models are imported before calling db.create_all()
        # This might require importing models from various blueprints if not already done
        from . import models # Ensure all models in models.py are loaded
        
        db.create_all()
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            try:
                os.makedirs(app.config['UPLOAD_FOLDER'])
                current_app.logger.info(f"Upload folder created at: {app.config['UPLOAD_FOLDER']}")
            except OSError as e:
                current_app.logger.error(f"Error creating upload folder {app.config['UPLOAD_FOLDER']}: {e}")
        
        # print(f"Database should be created at: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # Check if the database directory exists
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                # print(f"Created database directory: {db_dir}")
            except OSError as e:
                current_app.logger.error(f"Error creating database directory {db_dir}: {e}")
                
    return app
