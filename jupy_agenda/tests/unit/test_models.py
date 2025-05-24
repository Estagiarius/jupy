from jupy_agenda.tests.base_test import BaseTestCase
from jupy_agenda.app.models import User, Task # Import models to be tested
from jupy_agenda.app import db # To add objects to session for some tests if needed

class TestUserModel(BaseTestCase):

    def test_password_setter(self):
        u = User(username='testuser', email='test@example.com')
        u.set_password('cat')
        self.assertIsNotNone(u.password_hash)
        self.assertNotEqual(u.password_hash, 'cat')

    def test_password_checker(self):
        u = User(username='testuser2', email='test2@example.com')
        u.set_password('dog')
        self.assertTrue(u.check_password('dog'))
        self.assertFalse(u.check_password('cat'))

    def test_user_representation(self):
        u = User(username='testuser3', email='test3@example.com')
        self.assertEqual(repr(u), '<User testuser3>')

    def test_user_creation_with_db(self):
        # Test creating a user and adding to the session (optional, more like integration)
        initial_user_count = User.query.count()
        u = User(username='dbuser', email='db@example.com')
        u.set_password('securepassword')
        db.session.add(u)
        db.session.commit()
        
        self.assertEqual(User.query.count(), initial_user_count + 1)
        queried_user = User.query.filter_by(username='dbuser').first()
        self.assertIsNotNone(queried_user)
        self.assertEqual(queried_user.email, 'db@example.com')
        self.assertTrue(queried_user.check_password('securepassword'))
        
        # Clean up this specific user for other tests if BaseTestCase doesn't already clear all data
        # db.session.delete(queried_user)
        # db.session.commit()

class TestTaskModel(BaseTestCase):

    def test_task_priority_display(self):
        t1 = Task(description="Low priority task", priority=1)
        t2 = Task(description="Medium priority task", priority=2)
        t3 = Task(description="High priority task", priority=3)
        t4 = Task(description="Unknown priority task", priority=99) # Test default case
        
        self.assertEqual(t1.priority_display, 'Low')
        self.assertEqual(t2.priority_display, 'Medium')
        self.assertEqual(t3.priority_display, 'High')
        self.assertEqual(t4.priority_display, 'Unknown')

    def test_task_representation(self):
        # Need a user for a task, as user_id is not nullable.
        # Create a dummy user first, or assign an existing one if tests run sequentially and share context
        # For isolated unit tests, it's better to mock or set up minimal dependencies.
        # However, since we are using BaseTestCase, db is available.
        
        user = User(username='task_user_for_repr', email='task_user_repr@example.com')
        user.set_password('test')
        db.session.add(user)
        db.session.commit() # Commit to get user.id

        task = Task(user_id=user.id, description="A sample task for representation test", status="pending")
        # db.session.add(task)
        # db.session.commit() # Not strictly needed for repr if ID is not part of it, but good practice
        
        # Expected format: <Task {self.id}: {self.description[:30]}... (User: {self.user_id}, Status: {self.status})>
        # The ID might be None if not committed. For a pure unit test of repr, you might not need DB.
        # If ID is part of repr and can be None, handle that.
        # For this test, let's assume id is not critical for the part of repr we're checking or it's committed.
        
        # To get an ID for the task, we need to add and commit it.
        db.session.add(task)
        db.session.commit()

        expected_repr = f'<Task {task.id}: {task.description[:30]}... (User: {user.id}, Status: {task.status})>'
        self.assertEqual(repr(task), expected_repr)

        # Clean up
        # db.session.delete(task)
        # db.session.delete(user)
        # db.session.commit()

# Add more model tests here as needed for other models.
# For example, Event model, Reminder model default values, etc.
