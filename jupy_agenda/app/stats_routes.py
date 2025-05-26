from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from .services import statistics_service # Import the new service

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/')
@login_required
def statistics_page():
    """Displays the main statistics page."""
    user_id = current_user.id
    
    task_stats = statistics_service.get_task_completion_stats(user_id)
    event_stats = statistics_service.get_event_stats(user_id)
    
    # For charts - directly pass data to the template
    # Task Completion Pie Chart Data (Completed vs. Pending)
    task_completion_chart_data = {
        'labels': ['Completed Tasks', 'Pending Tasks'],
        'data': [task_stats.get('completed', 0), task_stats.get('pending', 0)]
    }
    
    # Event Distribution Pie Chart Data (Past vs. Upcoming)
    event_distribution_chart_data = {
        'labels': ['Past Events', 'Upcoming Events'],
        'data': [event_stats.get('past', 0), event_stats.get('upcoming', 0)]
    }
    
    # Monthly creation stats (optional, but implemented in service)
    monthly_tasks = statistics_service.get_monthly_task_creation_stats(user_id)
    monthly_events = statistics_service.get_monthly_event_creation_stats(user_id)
        
    return render_template('stats/statistics.html', 
                           title='Statistics & Reports',
                           task_stats=task_stats,
                           event_stats=event_stats,
                           task_completion_chart_data=task_completion_chart_data,
                           event_distribution_chart_data=event_distribution_chart_data,
                           monthly_tasks_chart_data=monthly_tasks, # Expects {'labels': [...], 'data': [...]}
                           monthly_events_chart_data=monthly_events) # Expects {'labels': [...], 'data': [...]}

# Example of a data endpoint (optional, if fetching data via JS later)
# @stats_bp.route('/data/task_completion')
# @login_required
# def task_completion_data():
#     stats = statistics_service.get_task_completion_stats(current_user.id)
#     return jsonify({
#         'labels': ['Completed', 'Pending', 'Overdue Pending'],
#         'data': [stats['completed'], stats['pending'], stats['overdue_pending']]
#     })
