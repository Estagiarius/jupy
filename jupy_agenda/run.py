from jupy_agenda.app import create_app, db
from jupy_agenda.app.models import Reminder, Event, Task, User # Import models for context
from jupy_agenda.app.services.notification_service import send_email_reminder
import os
import click # For Flask CLI
from datetime import datetime

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
