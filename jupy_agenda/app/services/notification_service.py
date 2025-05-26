from flask import current_app, render_template
from flask_mail import Message
from .. import mail, db # Access mail instance from app factory, and db
from ..models import Reminder, User, Event, Task # Import necessary models
from datetime import datetime

def send_email_reminder(reminder_id):
    """
    Sends an email for a given reminder.
    Updates the reminder's status based on the outcome.
    """
    app = current_app._get_current_object() # Get the actual app instance for context
    if not app:
        # This might happen if called outside of an app context, though Flask-CLI should provide one.
        print("Error: Application context not found.")
        return False

    with app.app_context(): # Ensure we're in an application context
        reminder = Reminder.query.get(reminder_id)
        if not reminder:
            app.logger.error(f"Reminder with ID {reminder_id} not found.")
            return False

        if reminder.sent_status != 'pending':
            app.logger.info(f"Reminder {reminder_id} is not pending (status: {reminder.sent_status}). Skipping.")
            return False

        user = User.query.get(reminder.user_id)
        if not user:
            app.logger.error(f"User {reminder.user_id} for reminder {reminder_id} not found.")
            reminder.sent_status = 'error'
            db.session.commit()
            return False

        item = None
        template_base = None
        subject = ""

        if reminder.item_type == 'event':
            item = Event.query.get(reminder.item_id)
            template_base = 'email/event_reminder'
            subject = f"Event Reminder: {item.title if item else 'N/A'}"
        elif reminder.item_type == 'task':
            item = Task.query.get(reminder.item_id)
            template_base = 'email/task_reminder'
            subject = f"Task Reminder: {item.description[:30] if item else 'N/A'}..."
        else:
            app.logger.error(f"Unknown item_type '{reminder.item_type}' for reminder {reminder_id}.")
            reminder.sent_status = 'error'
            db.session.commit()
            return False

        if not item:
            app.logger.error(f"{reminder.item_type.capitalize()} with ID {reminder.item_id} for reminder {reminder_id} not found.")
            reminder.sent_status = 'error'
            db.session.commit()
            return False
        
        # Check if user has an email (User model should have an email field)
        if not user.email:
            app.logger.error(f"User {user.id} has no email address for reminder {reminder.id}.")
            reminder.sent_status = 'error'
            db.session.commit()
            return False

        try:
            msg = Message(
                subject,
                sender=app.config.get('MAIL_DEFAULT_SENDER', 'noreply@jupy.agenda'),
                recipients=[user.email]
            )
            msg.body = render_template(template_base + '.txt', user=user, item=item)
            msg.html = render_template(template_base + '.html', user=user, item=item)
            
            if app.config.get('MAIL_SUPPRESS_SEND', False):
                # If MAIL_SUPPRESS_SEND is True, Flask-Mail's send() is a no-op.
                # We can log the email content for debugging if needed.
                app.logger.info(f"MAIL_SUPPRESS_SEND is True. Email for reminder {reminder.id} to {user.email} would be: \nSubject: {msg.subject}\nBody:\n{msg.body}")
                mail.send(msg) # This will be a no-op but good to call to ensure flow.
            else:
                mail.send(msg)
                app.logger.info(f"Sent reminder {reminder.id} to {user.email} for {reminder.item_type} {item.id}")

            reminder.sent_status = 'sent'
            reminder.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            app.logger.error(f"Error sending email for reminder {reminder.id} to {user.email}: {e}")
            reminder.sent_status = 'error'
            reminder.updated_at = datetime.utcnow()
            db.session.commit()
            return False
