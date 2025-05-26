import unittest
import os
from jupy_agenda.app import create_app, db
from jupy_agenda.tests.test_config import TestConfig

class BaseTestCase(unittest.TestCase):
    """Base TestCase for setting up and tearing down the test environment."""

    @classmethod
    def setUpClass(cls):
        """Set up for all tests in the class."""
        cls.app = create_app(config_class=TestConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Ensure the test upload folder exists if any tests perform actual file uploads
        if not os.path.exists(cls.app.config['UPLOAD_FOLDER']):
            try:
                os.makedirs(cls.app.config['UPLOAD_FOLDER'])
            except OSError as e:
                print(f"Error creating test upload folder {cls.app.config['UPLOAD_FOLDER']}: {e}")
        
        db.create_all()
        
    @classmethod
    def tearDownClass(cls):
        """Tear down after all tests in the class."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

        # Clean up test upload folder if it was created and is empty
        # This is a basic cleanup. For more robust cleanup, especially if files are created,
        # you might need to iterate and delete files/subfolders.
        try:
            if os.path.exists(cls.app.config['UPLOAD_FOLDER']) and not os.listdir(cls.app.config['UPLOAD_FOLDER']):
                os.rmdir(cls.app.config['UPLOAD_FOLDER'])
            elif os.path.exists(cls.app.config['UPLOAD_FOLDER']): # If not empty, log or handle as needed
                 # Example: shutil.rmtree(cls.app.config['UPLOAD_FOLDER']) for recursive delete
                 pass # For now, leave non-empty test_uploads folder
        except OSError as e:
            print(f"Error removing test upload folder {cls.app.config['UPLOAD_FOLDER']}: {e}")


    def setUp(self):
        """Set up for each test method."""
        # self.client is often created per test method or per class
        # If created per method, it ensures a fresh client for each test.
        # If per class, ensure tests don't interfere with each other's client state (e.g., session).
        self.client = self.app.test_client()
        
        # You might want to start a transaction here if your tests modify the DB
        # and you want to roll back after each test.
        # For simplicity, we'll rely on setUpClass/tearDownClass for full DB setup/teardown.

    def tearDown(self):
        """Tear down after each test method."""
        # If you started a transaction in setUp, roll it back here.
        # db.session.rollback() 
        pass

if __name__ == '__main__':
    unittest.main()
