from jupy_agenda.tests.base_test import BaseTestCase
from jupy_agenda.app.models import User
from jupy_agenda.app import db
from flask import get_flashed_messages, session

class TestAuthRoutes(BaseTestCase):

    def _register_user(self, username="testuser", email="test@example.com", password="password123"):
        return self.client.post('/auth/register', data=dict(
            username=username,
            email=email,
            password=password,
            confirm_password=password
        ), follow_redirects=True)

    def _login_user(self, email="test@example.com", password="password123"):
        return self.client.post('/auth/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def test_register_page_loads(self):
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_user_registration_successful(self):
        with self.client: # Use client as context manager to handle session cookies
            response = self._register_user()
            self.assertEqual(response.status_code, 200) # Should redirect to index
            self.assertIn(b'Welcome to Jupy Agenda', response.data) # Assuming index page content
            
            # Check flashed message (requires session and request context)
            # Flashed messages are tricky to test directly without a request context
            # However, we can check if user is in DB and logged in
            
            user = User.query.filter_by(email="test@example.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "testuser")

            # Check if user is logged in (current_user is set in session)
            # This requires the test client to maintain session state
            self.assertTrue(session.get('_user_id') is not None)
            self.assertEqual(int(session['_user_id']), user.id)


    def test_user_registration_duplicate_username(self):
        self._register_user(username="existinguser", email="unique1@example.com")
        response = self._register_user(username="existinguser", email="unique2@example.com")
        self.assertIn(b'That username is already taken.', response.data)

    def test_user_registration_duplicate_email(self):
        self._register_user(username="uniqueuser1", email="existing@example.com")
        response = self._register_user(username="uniqueuser2", email="existing@example.com")
        self.assertIn(b'That email address is already registered.', response.data)

    def test_login_page_loads(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_user_login_successful(self):
        self._register_user(email="login@example.com", password="password123")
        # Logout first if registration auto-logs in (which it does in this app)
        self.client.get('/auth/logout', follow_redirects=True) 

        with self.client:
            response = self._login_user(email="login@example.com", password="password123")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Welcome to Jupy Agenda', response.data) # Assuming index content after login
            self.assertTrue(session.get('_user_id') is not None) # Check session

    def test_user_login_invalid_email(self):
        self._register_user(email="valid@example.com", password="password123")
        self.client.get('/auth/logout', follow_redirects=True)
        response = self._login_user(email="invalid@example.com", password="password123")
        self.assertIn(b'Login Unsuccessful. Please check email and password', response.data)

    def test_user_login_invalid_password(self):
        self._register_user(email="another@example.com", password="password123")
        self.client.get('/auth/logout', follow_redirects=True)
        response = self._login_user(email="another@example.com", password="wrongpassword")
        self.assertIn(b'Login Unsuccessful. Please check email and password', response.data)

    def test_user_logout(self):
        self._register_user(email="logout@example.com", password="password123")
        # User is logged in after registration
        
        with self.client:
            response = self.client.get('/auth/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Login', response.data) # Should redirect to login page
            self.assertTrue(session.get('_user_id') is None) # User should be logged out

    def test_access_protected_route_unauthenticated(self):
        response = self.client.get('/profile', follow_redirects=True) # Profile page requires login
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data) # Should be redirected to login
        self.assertIn(b'Please log in to access this page.', response.data) # Flashed message

    def test_access_protected_route_authenticated(self):
        with self.client:
            self._register_user(username="protected_user", email="protected@example.com")
            # User is now logged in
            response = self.client.get('/profile')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'User Profile', response.data)
            self.assertIn(b'protected_user', response.data) # Check if username is on profile page
            self.assertNotIn(b'Please log in to access this page.', response.data)

# Helper to get flashed messages (if needed, but can be complex with test client)
# def get_flashed_messages_from_response(response):
#     # This is a simplified way; a more robust way might involve inspecting session directly
#     # or using a custom test utility. Flask's get_flashed_messages needs a request context.
#     try:
#         # Attempt to parse HTML for flashed messages if they are rendered
#         # This is fragile and depends on your template structure
#         from bs4 import BeautifulSoup
#         soup = BeautifulSoup(response.data, 'html.parser')
#         alerts = soup.find_all(class_=lambda x: x and x.startswith('alert-'))
#         return [alert.get_text(strip=True) for alert in alerts]
#     except:
#         return []
