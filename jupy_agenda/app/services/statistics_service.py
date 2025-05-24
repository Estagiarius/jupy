from ..models import Task, Event, User
from .. import db
from datetime import datetime, date
from sqlalchemy import func, extract
from collections import OrderedDict

def get_task_completion_stats(user_id):
    """Calculates task completion statistics for a given user."""
    today = date.today()
    
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()
    pending_tasks = Task.query.filter_by(user_id=user_id, status='pending').count()
    
    # Overdue pending tasks: status is 'pending' and due_date is in the past
    overdue_pending_tasks = Task.query.filter(
        Task.user_id == user_id,
        Task.status == 'pending',
        Task.due_date != None, # Ensure due_date is not NULL
        Task.due_date < today
    ).count()
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'overdue_pending': overdue_pending_tasks
    }

def get_event_stats(user_id):
    """Calculates event statistics for a given user."""
    now = datetime.utcnow()
    
    total_events = Event.query.filter_by(user_id=user_id).count()
    
    # Past events: end_time is in the past
    past_events = Event.query.filter(
        Event.user_id == user_id,
        Event.end_time < now
    ).count()
    
    # Upcoming events: start_time is in the future
    upcoming_events = Event.query.filter(
        Event.user_id == user_id,
        Event.start_time >= now # Or > now, depending on definition of "upcoming"
    ).count()
    
    return {
        'total': total_events,
        'past': past_events,
        'upcoming': upcoming_events
    }

def get_monthly_task_creation_stats(user_id, months=6):
    """
    Calculates task creation statistics for the last N months.
    Returns a dictionary with 'labels' (YYYY-MM) and 'data' (counts).
    """
    labels = []
    data = []
    
    today = date.today()
    
    for i in range(months -1, -1, -1): # Iterate from 'months-1' months ago to current month
        # Calculate the first day of the target month
        year = today.year
        month = today.month - i
        
        # Adjust year and month if month goes below 1
        while month <= 0:
            month += 12
            year -= 1
            
        month_label = f"{year:04d}-{month:02d}"
        labels.append(month_label)
        
        # Count tasks created in that month and year
        count = db.session.query(func.count(Task.id)).filter(
            Task.user_id == user_id,
            extract('year', Task.created_at) == year,
            extract('month', Task.created_at) == month
        ).scalar()
        data.append(count)
        
    return {'labels': labels, 'data': data}


def get_monthly_event_creation_stats(user_id, months=6):
    """
    Calculates event creation statistics for the last N months.
    Returns a dictionary with 'labels' (YYYY-MM) and 'data' (counts).
    """
    labels = []
    data = []
    
    today = date.today()
    
    for i in range(months -1, -1, -1): # Iterate from 'months-1' months ago to current month
        year = today.year
        month = today.month - i

        while month <= 0:
            month += 12
            year -= 1
            
        month_label = f"{year:04d}-{month:02d}"
        labels.append(month_label)
        
        count = db.session.query(func.count(Event.id)).filter(
            Event.user_id == user_id,
            extract('year', Event.created_at) == year,
            extract('month', Event.created_at) == month
        ).scalar()
        data.append(count)
        
    return {'labels': labels, 'data': data}
