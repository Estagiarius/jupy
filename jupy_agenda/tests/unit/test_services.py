from jupy_agenda.tests.base_test import BaseTestCase
from jupy_agenda.app.models import User, Task, Event # Import models for creating test data
from jupy_agenda.app.services import statistics_service
from jupy_agenda.app import db
from datetime import datetime, date, timedelta

class TestStatisticsService(BaseTestCase):

    def setUp(self):
        super().setUp() # Call BaseTestCase.setUp to get self.client etc.
        
        # Create a test user
        self.user1 = User(username='stats_user1', email='stats1@example.com')
        self.user1.set_password('password123')
        
        self.user2 = User(username='stats_user2', email='stats2@example.com')
        self.user2.set_password('password456')
        
        db.session.add_all([self.user1, self.user2])
        db.session.commit() # Commit to get user IDs

        # Create sample tasks for user1
        self.task1_u1 = Task(user_id=self.user1.id, description="U1 Task 1", status="completed", due_date=date.today() - timedelta(days=1))
        self.task2_u1 = Task(user_id=self.user1.id, description="U1 Task 2", status="pending", due_date=date.today() + timedelta(days=5))
        self.task3_u1 = Task(user_id=self.user1.id, description="U1 Task 3", status="pending", due_date=date.today() - timedelta(days=2)) # Overdue
        self.task4_u1 = Task(user_id=self.user1.id, description="U1 Task 4", status="pending", due_date=date.today() + timedelta(days=1))
        
        # Create sample tasks for user2
        self.task1_u2 = Task(user_id=self.user2.id, description="U2 Task 1", status="completed")

        # Create sample events for user1
        now = datetime.utcnow()
        self.event1_u1 = Event(user_id=self.user1.id, title="U1 Event 1 Past", start_time=now - timedelta(days=2), end_time=now - timedelta(days=1))
        self.event2_u1 = Event(user_id=self.user1.id, title="U1 Event 2 Upcoming", start_time=now + timedelta(days=1), end_time=now + timedelta(days=2))
        self.event3_u1 = Event(user_id=self.user1.id, title="U1 Event 3 Also Upcoming", start_time=now + timedelta(hours=1), end_time=now + timedelta(hours=2))

        # Create sample events for user2
        self.event1_u2 = Event(user_id=self.user2.id, title="U2 Event 1 Past", start_time=now - timedelta(days=3), end_time=now - timedelta(days=2))

        db.session.add_all([
            self.task1_u1, self.task2_u1, self.task3_u1, self.task4_u1, self.task1_u2,
            self.event1_u1, self.event2_u1, self.event3_u1, self.event1_u2
        ])
        db.session.commit()

    def test_get_task_completion_stats(self):
        stats_u1 = statistics_service.get_task_completion_stats(self.user1.id)
        self.assertEqual(stats_u1['total'], 4)
        self.assertEqual(stats_u1['completed'], 1)
        self.assertEqual(stats_u1['pending'], 3)
        self.assertEqual(stats_u1['overdue_pending'], 1) # task3_u1

        stats_u2 = statistics_service.get_task_completion_stats(self.user2.id)
        self.assertEqual(stats_u2['total'], 1)
        self.assertEqual(stats_u2['completed'], 1)
        self.assertEqual(stats_u2['pending'], 0)
        self.assertEqual(stats_u2['overdue_pending'], 0)

    def test_get_event_stats(self):
        stats_u1 = statistics_service.get_event_stats(self.user1.id)
        self.assertEqual(stats_u1['total'], 3)
        self.assertEqual(stats_u1['past'], 1)    # event1_u1
        self.assertEqual(stats_u1['upcoming'], 2) # event2_u1, event3_u1

        stats_u2 = statistics_service.get_event_stats(self.user2.id)
        self.assertEqual(stats_u2['total'], 1)
        self.assertEqual(stats_u2['past'], 1)
        self.assertEqual(stats_u2['upcoming'], 0)

    def test_get_monthly_task_creation_stats(self):
        # For this test, we'll focus on user1. All tasks were created "now" (within setUp).
        # So, they should all fall into the current month.
        
        # Create tasks with specific creation dates for better testing
        db.session.delete(self.task1_u1) # remove task created 'now'
        db.session.delete(self.task2_u1)
        db.session.delete(self.task3_u1)
        db.session.delete(self.task4_u1)
        db.session.commit()

        today = date.today()
        first_of_this_month_dt = datetime(today.year, today.month, 1)
        
        # One task this month
        task_this_month = Task(user_id=self.user1.id, description="Task This Month", created_at=first_of_this_month_dt + timedelta(days=3))
        
        # Two tasks last month
        if today.month == 1:
            first_of_last_month_dt = datetime(today.year - 1, 12, 1)
        else:
            first_of_last_month_dt = datetime(today.year, today.month - 1, 1)
        
        task_last_month1 = Task(user_id=self.user1.id, description="Task Last Month 1", created_at=first_of_last_month_dt + timedelta(days=1))
        task_last_month2 = Task(user_id=self.user1.id, description="Task Last Month 2", created_at=first_of_last_month_dt + timedelta(days=5))

        db.session.add_all([task_this_month, task_last_month1, task_last_month2])
        db.session.commit()

        stats = statistics_service.get_monthly_task_creation_stats(self.user1.id, months=2) # Test for last 2 months
        
        # Expected labels: ['YYYY-MM (last month)', 'YYYY-MM (this month)']
        this_month_label = f"{today.year:04d}-{today.month:02d}"
        last_month_year = first_of_last_month_dt.year
        last_month_month = first_of_last_month_dt.month
        last_month_label = f"{last_month_year:04d}-{last_month_month:02d}"

        self.assertIn(this_month_label, stats['labels'])
        self.assertIn(last_month_label, stats['labels'])
        
        # Find index for assertions
        idx_this_month = stats['labels'].index(this_month_label)
        idx_last_month = stats['labels'].index(last_month_label)

        self.assertEqual(stats['data'][idx_this_month], 1) # One task this month
        self.assertEqual(stats['data'][idx_last_month], 2) # Two tasks last month

    def test_get_monthly_event_creation_stats(self):
        # Similar logic to task creation stats, adjust if needed for events
        db.session.delete(self.event1_u1)
        db.session.delete(self.event2_u1)
        db.session.delete(self.event3_u1)
        db.session.commit()

        today = date.today()
        first_of_this_month_dt = datetime(today.year, today.month, 1)
        event_this_month = Event(user_id=self.user1.id, title="Event This Month", start_time=datetime.now(), end_time=datetime.now(), created_at=first_of_this_month_dt + timedelta(days=2))
        db.session.add(event_this_month)
        db.session.commit()

        stats = statistics_service.get_monthly_event_creation_stats(self.user1.id, months=1)
        this_month_label = f"{today.year:04d}-{today.month:02d}"
        self.assertEqual(stats['labels'], [this_month_label])
        self.assertEqual(stats['data'], [1])
