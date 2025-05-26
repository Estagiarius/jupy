from jupy_agenda.tests.base_test import BaseTestCase
from jupy_agenda.app.models import User, Task
from jupy_agenda.app import db
from datetime import date, timedelta

class TestTaskRoutes(BaseTestCase):

    def setUp(self):
        super().setUp() # This creates self.client
        # Register and log in a user for these tests
        with self.client: # Use client as context manager to ensure session persistence
            self.client.post('/auth/register', data=dict(
                username='tasktestuser',
                email='tasktest@example.com',
                password='password'
            ), follow_redirects=True)
            # The user is logged in after registration.
            # Store user for creating tasks associated with this user
            self.user = User.query.filter_by(email='tasktest@example.com').first()
            self.assertIsNotNone(self.user, "Test user setup failed: user not found in DB after registration.")


    def test_task_list_page_loads(self):
        response = self.client.get('/todo/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My To-Do List', response.data)

    def test_add_task_page_loads(self):
        response = self.client.get('/todo/task/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Task', response.data) # Legend for new task form

    def test_add_task_successful(self):
        with self.client:
            response = self.client.post('/todo/task/add', data=dict(
                description='Test adding a new task',
                due_date=(date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                priority='2', # Medium
                status='pending'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Task created successfully!', response.data) # Flashed message
            self.assertIn(b'Test adding a new task', response.data) # Task should be in the list
            
            task = Task.query.filter_by(description='Test adding a new task').first()
            self.assertIsNotNone(task)
            self.assertEqual(task.user_id, self.user.id)
            self.assertEqual(task.priority, 2)

    def test_add_task_missing_description(self):
        with self.client:
            response = self.client.post('/todo/task/add', data=dict(
                description='', # Missing description
                priority='1',
                status='pending'
            ), follow_redirects=True)
            self.assertEqual(response.status_code, 200) # Stays on form page
            self.assertIn(b'This field is required.', response.data) # WTForms error message

    def test_edit_task(self):
        # First, add a task to edit
        task_to_edit = Task(user_id=self.user.id, description="Task to be edited", priority=1, status="pending")
        db.session.add(task_to_edit)
        db.session.commit()
        self.assertIsNotNone(task_to_edit.id, "Task ID should not be None after commit")

        with self.client:
            # Test GET request for edit page
            response_get = self.client.get(f'/todo/task/edit/{task_to_edit.id}')
            self.assertEqual(response_get.status_code, 200)
            self.assertIn(b'Edit Task', response_get.data)
            self.assertIn(b'Task to be edited', response_get.data) # Original description

            # Test POST request to update the task
            updated_description = "Task has been updated successfully"
            updated_priority = 3 # High
            response_post = self.client.post(f'/todo/task/edit/{task_to_edit.id}', data=dict(
                description=updated_description,
                due_date=task_to_edit.due_date.strftime('%Y-%m-%d') if task_to_edit.due_date else '',
                priority=str(updated_priority),
                status=task_to_edit.status
            ), follow_redirects=True)
            
            self.assertEqual(response_post.status_code, 200)
            self.assertIn(b'Task updated successfully!', response_post.data)
            self.assertIn(bytes(updated_description, 'utf-8'), response_post.data) # Updated description in list

            edited_task = Task.query.get(task_to_edit.id)
            self.assertEqual(edited_task.description, updated_description)
            self.assertEqual(edited_task.priority, updated_priority)

    def test_delete_task(self):
        task_to_delete = Task(user_id=self.user.id, description="Task to be deleted", priority=1, status="pending")
        db.session.add(task_to_delete)
        db.session.commit()
        task_id = task_to_delete.id
        self.assertIsNotNone(task_id, "Task ID should not be None for deletion test")

        with self.client:
            response = self.client.post(f'/todo/task/delete/{task_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Task deleted successfully!', response.data)
            self.assertNotIn(b'Task to be deleted', response.data) # Task should no longer be in list

            deleted_task = Task.query.get(task_id)
            self.assertIsNone(deleted_task)

    def test_update_task_status(self):
        task_to_update = Task(user_id=self.user.id, description="Task for status update", priority=1, status="pending")
        db.session.add(task_to_update)
        db.session.commit()
        task_id = task_to_update.id

        with self.client:
            response = self.client.post(f'/todo/task/update_status/{task_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'marked as completed!', response.data)
            
            updated_task = Task.query.get(task_id)
            self.assertEqual(updated_task.status, 'completed')

            # Toggle back to pending
            response_toggle_back = self.client.post(f'/todo/task/update_status/{task_id}', follow_redirects=True)
            self.assertEqual(response_toggle_back.status_code, 200)
            self.assertIn(b'marked as pending!', response_toggle_back.data)
            
            updated_task_again = Task.query.get(task_id)
            self.assertEqual(updated_task_again.status, 'pending')

    def test_task_ownership(self):
        # Create another user
        other_user = User(username="otheruser", email="other@example.com", password_hash="otherpassword")
        other_user.set_password("otherpassword")
        db.session.add(other_user)
        db.session.commit()

        # Create a task for the other user
        other_user_task = Task(user_id=other_user.id, description="Other user's task", priority=1, status="pending")
        db.session.add(other_user_task)
        db.session.commit()
        other_task_id = other_user_task.id

        with self.client: # self.user (tasktestuser) is logged in
            # Try to access edit page of other_user_task
            response_get_edit = self.client.get(f'/todo/task/edit/{other_task_id}')
            self.assertEqual(response_get_edit.status_code, 403) # Forbidden

            # Try to post an edit to other_user_task
            response_post_edit = self.client.post(f'/todo/task/edit/{other_task_id}', data=dict(
                description="Attempted malicious edit", priority="1", status="pending"
            ), follow_redirects=True)
            self.assertEqual(response_post_edit.status_code, 403)

            # Try to delete other_user_task
            response_delete = self.client.post(f'/todo/task/delete/{other_task_id}', follow_redirects=True)
            self.assertEqual(response_delete.status_code, 403)
            
            # Try to update status of other_user_task
            response_update_status = self.client.post(f'/todo/task/update_status/{other_task_id}', follow_redirects=True)
            self.assertEqual(response_update_status.status_code, 403)

            # Verify the other user's task was not affected
            unaffected_task = Task.query.get(other_task_id)
            self.assertIsNotNone(unaffected_task)
            self.assertEqual(unaffected_task.description, "Other user's task")
