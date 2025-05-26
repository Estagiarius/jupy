from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from .forms import EventForm
from .models import User, Event, Reminder # Ensure Reminder is imported
from . import db
from datetime import datetime, date, timedelta # Ensure timedelta is imported
import calendar

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@calendar_bp.route('/calendar/<int:year>/<int:month>')
@login_required
def month_view(year=None, month=None):
    """Displays the calendar for a given month and year, or current month."""
    today = date.today()
    if year is None or month is None:
        year, month = today.year, today.month
    
    # Validate year and month (basic validation)
    if not (1 <= month <= 12):
        flash('Mês inválido especificado. Redirecionando para o mês atual.', 'warning')
        return redirect(url_for('calendar.month_view', year=today.year, month=today.month))
    if not (1900 <= year <= 2100): # Arbitrary range, adjust as needed
        flash('Ano inválido especificado. Redirecionando para o mês atual.', 'warning')
        return redirect(url_for('calendar.month_view', year=today.year, month=today.month))

    # Create a calendar object
    cal = calendar.Calendar() # Default is Monday first day of week
    month_days = cal.monthdatescalendar(year, month) # List of weeks (each week is a list of datetime.date objects)

    # Fetch events for the current user for the displayed month
    # Get the first day of the month and the first day of the next month
    first_day_of_month = date(year, month, 1)
    if month == 12:
        first_day_of_next_month = date(year + 1, 1, 1)
    else:
        first_day_of_next_month = date(year, month + 1, 1)

    events_query = Event.query.filter(
        Event.user_id == current_user.id,
        Event.start_time >= first_day_of_month,
        Event.start_time < first_day_of_next_month
    ).order_by(Event.start_time).all()

    # Organize events by day for easy lookup in the template
    events_by_day = {}
    for event in events_query:
        event_date = event.start_time.date()
        if event_date not in events_by_day:
            events_by_day[event_date] = []
        events_by_day[event_date].append(event)

    # Previous and next month logic
    prev_month_date = date(year, month, 1) - timedelta(days=1) # Go to last day of prev month
    next_month_date = first_day_of_next_month 

    return render_template('calendar/calendar_view.html', 
                           title=f"Calendar - {calendar.month_name[month]} {year}",
                           year=year, 
                           month=month, 
                           month_days=month_days, # a list of lists of date objects
                           events_by_day=events_by_day,
                           current_user=current_user,
                           today=today,
                           prev_year=prev_month_date.year,
                           prev_month=prev_month_date.month,
                           next_year=next_month_date.year,
                           next_month=next_month_date.month,
                           month_name=calendar.month_name[month])


@calendar_bp.route('/event/delete/<int:event_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_event(event_id):
    """Handles deleting an event."""
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        year, month = event.start_time.year, event.start_time.month
        db.session.delete(event)
        db.session.commit()
        flash('Evento excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir evento: {e}', 'danger')
    
    return redirect(url_for('calendar.month_view', year=year, month=month))


# Helper function to manage reminders for events
def _update_event_reminder(event):
    """
    Deletes existing pending reminders for an event and creates a new one
    if the event's start_time is in the future.
    Reminder is set for 1 hour before the event.
    """
    try:
        # Delete existing pending reminders for this event
        Reminder.query.filter_by(user_id=event.user_id, item_type='event', item_id=event.id, sent_status='pending').delete()
        
        if event.start_time > datetime.utcnow() + timedelta(minutes=5): # Only if event is in future (plus a small buffer)
            reminder_time = event.start_time - timedelta(hours=1)
            if reminder_time > datetime.utcnow(): # Ensure reminder time itself is in the future
                new_reminder = Reminder(
                    user_id=event.user_id,
                    item_type='event',
                    item_id=event.id,
                    reminder_time=reminder_time,
                    notification_method='email' # Default, could be configurable later
                )
                db.session.add(new_reminder)
                # db.session.commit() will be called in the main route
                current_app.logger.info(f"Created reminder for event {event.id} at {reminder_time}")
            else:
                current_app.logger.info(f"Reminder time for event {event.id} would be in the past. No reminder created.")
        else:
            current_app.logger.info(f"Event {event.id} is in the past or too soon. No reminder created/updated.")
            
    except Exception as e:
        current_app.logger.error(f"Error updating event reminder for event {event.id}: {e}")
        # Don't let reminder logic break the main operation, but log it.
        # db.session.rollback() might be needed if this was part of a larger transaction that should fail.
        # However, add_event and edit_event handle their own rollbacks.
        pass # Silently fail for now, error is logged.

@calendar_bp.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    """Handles adding a new event."""
    form = EventForm()
    if form.validate_on_submit():
        try:
            new_event = Event(
                user_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(new_event)
            db.session.flush() # Flush to get new_event.id for reminder
            _update_event_reminder(new_event) # Add reminder logic
            db.session.commit()
            flash('Evento criado com sucesso!', 'success')
            return redirect(url_for('calendar.month_view', year=form.start_time.data.year, month=form.start_time.data.month))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar evento: {e}', 'danger')
    return render_template('calendar/event_form.html', title='Add Event', form=form, legend='New Event')


@calendar_bp.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Handles editing an existing event."""
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        abort(403) # Forbidden

    form = EventForm(obj=event) 
    if form.validate_on_submit():
        try:
            event.title = form.title.data
            event.description = form.description.data
            event.start_time = form.start_time.data
            event.end_time = form.end_time.data
            _update_event_reminder(event) # Add/Update reminder logic
            db.session.commit()
            flash('Evento atualizado com sucesso!', 'success')
            return redirect(url_for('calendar.month_view', year=event.start_time.year, month=event.start_time.month))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar evento: {e}', 'danger')
            
    return render_template('calendar/event_form.html', title='Edit Event', form=form, legend=f'Edit "{event.title}"', event_id=event.id)
