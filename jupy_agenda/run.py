from jupy_agenda.app import create_app, db
from jupy_agenda.app.models import Reminder, Event, Task, User # Import models for context
from jupy_agenda.app.services.notification_service import send_email_reminder
import os
import click # For Flask CLI
from datetime import datetime
import sys # For test runner
import unittest # For test runner

# Create the Flask app using the factory function
app = create_app()

# Flask CLI command to send reminders
@app.cli.command("send-reminders")
def send_reminders_command():
    """
    Processes and sends pending reminders.
    This command should be run periodically by a scheduler (e.g., cron).
    """
    with app.app_context(): # Ensure app context for db and mail
        current_time = datetime.utcnow()
        pending_reminders = Reminder.query.filter(
            Reminder.reminder_time <= current_time,
            Reminder.sent_status == 'pending'
        ).order_by(Reminder.reminder_time).all()

        if not pending_reminders:
            click.echo("No pending reminders to send.")
            app.logger.info("No pending reminders to send.")
            return

        click.echo(f"Found {len(pending_reminders)} pending reminders. Processing...")
        app.logger.info(f"Found {len(pending_reminders)} pending reminders. Processing...")
        
        sent_count = 0
        error_count = 0

        for reminder in pending_reminders:
            click.echo(f"Processing reminder ID: {reminder.id} for item {reminder.item_type} {reminder.item_id}...")
            app.logger.info(f"Processing reminder ID: {reminder.id} for item {reminder.item_type} {reminder.item_id}...")
            try:
                # Ensure the related item and user still exist
                related_item = None
                if reminder.item_type == 'event':
                    related_item = Event.query.get(reminder.item_id)
                elif reminder.item_type == 'task':
                    related_item = Task.query.get(reminder.item_id)
                
                user = User.query.get(reminder.user_id)

                if not related_item:
                    click.echo(f"  Item {reminder.item_type} {reminder.item_id} for reminder {reminder.id} not found. Marking as error.")
                    app.logger.warning(f"Item {reminder.item_type} {reminder.item_id} for reminder {reminder.id} not found. Marking as error.")
                    reminder.sent_status = 'error'
                    reminder.updated_at = datetime.utcnow()
                    db.session.commit()
                    error_count += 1
                    continue
                
                if not user:
                    click.echo(f"  User {reminder.user_id} for reminder {reminder.id} not found. Marking as error.")
                    app.logger.warning(f"User {reminder.user_id} for reminder {reminder.id} not found. Marking as error.")
                    reminder.sent_status = 'error'
                    reminder.updated_at = datetime.utcnow()
                    db.session.commit()
                    error_count += 1
                    continue

                if send_email_reminder(reminder.id):
                    click.echo(f"  Successfully sent reminder ID: {reminder.id}")
                    app.logger.info(f"Successfully sent reminder ID: {reminder.id}")
                    sent_count += 1
                else:
                    click.echo(f"  Failed to send reminder ID: {reminder.id}. Status set to 'error'.")
                    app.logger.error(f"Failed to send reminder ID: {reminder.id}. Status already set to 'error' by send_email_reminder.")
                    error_count += 1 # Status is updated in send_email_reminder
            except Exception as e:
                click.echo(f"  An unexpected error occurred processing reminder {reminder.id}: {e}")
                app.logger.error(f"An unexpected error occurred processing reminder {reminder.id}: {e}", exc_info=True)
                reminder.sent_status = 'error' # Ensure status is marked
                reminder.updated_at = datetime.utcnow()
                db.session.commit()
                error_count += 1
        
        click.echo(f"Reminder processing complete. Sent: {sent_count}, Errors: {error_count}.")
        app.logger.info(f"Reminder processing complete. Sent: {sent_count}, Errors: {error_count}.")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        """Runs the unit and functional tests."""
        # Ensure app context is available if tests need it globally,
        # though BaseTestCase should handle its own context.
        # For test discovery, it's generally better if tests manage their own app context.
        
        # Set FLASK_ENV to 'testing' or ensure TestConfig is used by default in tests
        # os.environ['FLASK_ENV'] = 'testing' # This might be another way to signal test mode

        # Discover and run tests from the 'jupy_agenda.tests' directory
        # Note: We are in jupy_agenda/run.py, so 'jupy_agenda.tests' should work if run from project root.
        # If run.py is in jupy_agenda/, then tests are in jupy_agenda/tests.
        # The discover path should be relative to the project root or an importable package path.
        # For simplicity, assuming 'jupy_agenda.tests' is discoverable.
        # If you run `python jupy_agenda/run.py test` from the project root.
        
        # Adjust the discovery path if your project structure or execution path differs.
        # 'jupy_agenda.tests' means it will look for a package named 'jupy_agenda.tests'.
        # If tests are directly under a 'tests' folder at the same level as 'jupy_agenda' package,
        # then discover('tests', pattern='test_*.py') from the project root is common.
        # Given the structure is jupy_agenda/tests, we'll use that.
        
        # This assumes that 'jupy_agenda' is in PYTHONPATH or the script is run from one level above 'jupy_agenda'
        # or 'jupy_agenda' itself is the current working directory.
        # Let's make it discover 'jupy_agenda/tests' directly.
        
        # The TestLoader().discover method takes the start directory as the first argument.
        # If run.py is in jupy_agenda/, then 'tests' refers to jupy_agenda/tests/.
        loader = unittest.TestLoader()
        # Discover tests in the 'jupy_agenda/tests' directory
        # The path should be relative to the project root if you run from project root.
        # If `run.py` is in `jupy_agenda/`, then `tests` is a sibling directory.
        # Let's assume the tests are in a package `jupy_agenda.tests`
        # And that `jupy_agenda` is the root for these imports.
        # The current working directory when running `python jupy_agenda/run.py test` is `jupy_agenda`.
        # So, `tests` is a subdirectory.
        
        # We need to make sure that the app context is pushed BEFORE tests are run
        # if the tests themselves don't manage it. BaseTestCase does manage it.
        
        # The test discovery should find tests in jupy_agenda/tests/unit and jupy_agenda/tests/functional
        # The pattern 'test_*.py' is standard.
        # The start_dir should be 'jupy_agenda.tests' if we want to use dot notation for package
        # or 'jupy_agenda/tests' if using file path.
        # Let's use file path relative to current run.py location
        # If run.py is in jupy_agenda/, and tests in jupy_agenda/tests/, then start_dir is 'tests'
        
        # Assuming run.py is in the root `jupy_agenda` directory, and tests are in `jupy_agenda/tests`
        # This means `tests` is a sub-package of `jupy_agenda`.
        # The command `python jupy_agenda/run.py test` is run from the parent of `jupy_agenda` directory.
        # So, the path for discovery should be 'jupy_agenda/tests' relative to project root.
        
        # The `discover` method's `start_dir` is a directory path.
        # If `run.py` is at `project_root/jupy_agenda/run.py`, and tests are at `project_root/jupy_agenda/tests`,
        # then the path from `run.py` to `tests` is just `tests`.
        # However, unittest.discover works best if `start_dir` is a package that can be imported.
        # Let's try to make `jupy_agenda.tests` importable.
        # This means the parent of `jupy_agenda` should be in `sys.path`.
        
        # For simplicity, let's assume the script is run from the project root (parent of jupy_agenda folder)
        # Example: `python -m jupy_agenda.run test` or `python jupy_agenda/run.py test`
        # In this case, `jupy_agenda.tests` should be importable.
        
        # Assuming `run.py` is in the `jupy_agenda` directory, and `tests` is a subdirectory.
        # The current working directory when `python jupy_agenda/run.py test` is executed
        # is typically the directory where `run.py` resides, i.e., `jupy_agenda`.
        # So, `tests` is a direct subdirectory.
        
        # The path to the tests directory relative to the location of run.py
        # If run.py is at /app/jupy_agenda/run.py, then tests_dir is /app/jupy_agenda/tests
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        tests_dir = os.path.join(current_script_dir, 'tests')


        if not os.path.isdir(tests_dir):
            click.echo(f"Tests directory not found at {tests_dir}. Ensure your tests are in jupy_agenda/tests.")
            sys.exit(1)
            
        click.echo(f"Looking for tests in: {tests_dir}")
        test_suite = loader.discover(start_dir=tests_dir, pattern='test_*.py')
        
        if test_suite.countTestCases() == 0:
            click.echo(f"No tests found in {tests_dir} with pattern 'test_*.py'.")
            click.echo("Please check your test file names and locations.")
            # List contents of tests_dir and subdirs for debugging
            for root, dirs, files in os.walk(tests_dir):
                click.echo(f"Found in {root}: dirs={dirs}, files={files}")
            sys.exit(1)

        click.echo(f"Running {test_suite.countTestCases()} tests...")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        if result.wasSuccessful():
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        # Ensure the database directory exists (though create_app also attempts this)
        db_dir = os.path.join(os.path.dirname(__file__), 'database')
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                print(f"Database directory created at: {db_dir}")
            except OSError as e:
                print(f"Error creating database directory {db_dir}: {e}")

        # The database tables are created within create_app()
        # For debugging, you can check the db URI
        print(f"Attempting to run app with database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        # Run the Flask development server
        # Host '0.0.0.0' makes it accessible from outside the container/VM if needed
        # Debug=True is useful for development, but should be False in production
        app.run(host='0.0.0.0', port=5000, debug=True)
    # Ensure the database directory exists (though create_app also attempts this)
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
            print(f"Database directory created at: {db_dir}")
        except OSError as e:
            print(f"Error creating database directory {db_dir}: {e}")

    # The database tables are created within create_app()
    # For debugging, you can check the db URI
    print(f"Attempting to run app with database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Run the Flask development server
    # Host '0.0.0.0' makes it accessible from outside the container/VM if needed
    # Debug=True is useful for development, but should be False in production
    app.run(host='0.0.0.0', port=5000, debug=True)
