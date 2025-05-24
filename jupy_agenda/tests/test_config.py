import os

class TestConfig:
    """Flask configuration for testing."""
    TESTING = True
    SECRET_KEY = os.environ.get('TEST_SECRET_KEY', 'test_secret_key_123!')
    
    # Use an in-memory SQLite database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Disable CSRF protection for tests (makes form testing easier)
    WTF_CSRF_ENABLED = False
    
    # Mail configuration for tests
    MAIL_SUPPRESS_SEND = True # Don't send emails during tests
    MAIL_DEFAULT_SENDER = 'test-noreply@jupy.agenda'

    # Upload folder - can be a temporary directory or a specific test uploads folder
    # For simplicity, we can use a temporary one or just ensure models don't rely on actual file storage
    # For tests involving file uploads, you might need a more robust setup with a temp folder.
    # For now, we'll assume tests might not perform actual file saves or will mock them.
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'test_uploads') # Example path

    # Make login manager behavior simpler for tests
    LOGIN_DISABLED = False # Ensure login is not globally disabled, use test client for sessions

    # Other configurations that might be relevant for testing
    # e.g., if you have rate limiting, disable it for tests.
    # If you use external services, mock them or use test instances.

# To ensure the test upload folder exists (if you were to do actual file uploads in tests)
# if not os.path.exists(TestConfig.UPLOAD_FOLDER):
#     os.makedirs(TestConfig.UPLOAD_FOLDER)
