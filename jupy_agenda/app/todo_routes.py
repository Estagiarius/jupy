from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user
from .forms import TaskForm
from .models import Task, Reminder # Ensure Reminder is imported
from . import db
from datetime import date, datetime, time, timedelta # Ensure datetime, time, timedelta are imported

todo_bp = Blueprint('todo', __name__)

@todo_bp.route('/list')
@todo_bp.route('/') # Default to list view
@login_required
def list_tasks():
    """Displays the list of tasks for the current user with filtering and sorting."""
    status_filter = request.args.get('status', None) # e.g., 'pending', 'completed'
    sort_by = request.args.get('sort_by', 'priority') # e.g., 'priority', 'due_date'

    tasks_query = Task.query.filter_by(user_id=current_user.id)

    if status_filter and status_filter in ['pending', 'completed']:
        tasks_query = tasks_query.filter(Task.status == status_filter)

    if sort_by == 'due_date':
        tasks_query = tasks_query.order_by(Task.due_date.asc().nullslast(), Task.priority.desc()) # Nulls last for due_date
    elif sort_by == 'priority':
        tasks_query = tasks_query.order_by(Task.priority.desc(), Task.due_date.asc().nullslast())
    else: # Default sort
        tasks_query = tasks_query.order_by(Task.created_at.desc())

    tasks = tasks_query.all()
    
    return render_template('todo/task_list.html', 
                           title='My To-Do List', 
                           tasks=tasks,
                           current_status_filter=status_filter,
                           current_sort_by=sort_by)

@todo_bp.route('/task/delete/<int:task_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_task(task_id):
    """Handles deleting a task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarefa excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir tarefa: {e}', 'danger')
    
    return redirect(url_for('todo.list_tasks'))

@todo_bp.route('/task/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    """Toggles the status of a task (e.g., pending <-> completed)."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)

    try:
        if task.status == 'pending':
            task.status = 'completed'
            flash(f'Tarefa "{task.description[:30]}..." marcada como concluída!', 'success')
        elif task.status == 'completed':
            task.status = 'pending'
            flash(f'Tarefa "{task.description[:30]}..." marcada como pendente!', 'info')
        else:
            # Handle other statuses if any, or default to pending
            task.status = 'pending'
            flash(f'Status da tarefa "{task.description[:30]}..." redefinido para pendente.', 'info')
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar status da tarefa: {e}', 'danger')
        
    return redirect(request.referrer or url_for('todo.list_tasks')) # Redirect to previous page or list


# Helper function to manage reminders for tasks
def _update_task_reminder(task):
    """
    Deletes existing pending reminders for a task and creates a new one
    if the task's due_date is set and in the future.
    Reminder is set for 9 AM on the due_date.
    """
    try:
        # Delete existing pending reminders for this task
        Reminder.query.filter_by(user_id=task.user_id, item_type='task', item_id=task.id, sent_status='pending').delete()

        if task.due_date and task.due_date >= date.today() + timedelta(days=0): # Only if task due_date is today or in future
            # Combine due_date with 9 AM to create reminder_datetime
            reminder_datetime = datetime.combine(task.due_date, time(9, 0, 0)) # 9 AM on due_date
            
            if reminder_datetime > datetime.utcnow(): # Ensure reminder time itself is in the future
                new_reminder = Reminder(
                    user_id=task.user_id,
                    item_type='task',
                    item_id=task.id,
                    reminder_time=reminder_datetime,
                    notification_method='email' # Default
                )
                db.session.add(new_reminder)
                current_app.logger.info(f"Created reminder for task {task.id} at {reminder_datetime}")
            else:
                current_app.logger.info(f"Reminder time for task {task.id} ({reminder_datetime}) would be in the past. No reminder created.")
        else:
            current_app.logger.info(f"Task {task.id} has no due date, or due date is in the past. No reminder created/updated.")
            
    except Exception as e:
        current_app.logger.error(f"Error updating task reminder for task {task.id}: {e}")
        pass # Silently fail for now, error is logged.


@todo_bp.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """Handles adding a new task."""
    form = TaskForm()
    if request.method == 'GET':
        form.priority.data = 1 
        form.status.data = 'pending'

    if form.validate_on_submit():
        try:
            new_task = Task(
                user_id=current_user.id,
                description=form.description.data,
                due_date=form.due_date.data,
                priority=form.priority.data,
                status=form.status.data
            )
            db.session.add(new_task)
            db.session.flush() # Flush to get new_task.id
            _update_task_reminder(new_task) # Add reminder logic
            db.session.commit()
            flash('Tarefa criada com sucesso!', 'success')
            return redirect(url_for('todo.list_tasks'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar tarefa: {e}', 'danger')
    return render_template('todo/task_form.html', title='Add Task', form=form, legend='New Task')

@todo_bp.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Handles editing an existing task."""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403) # Forbidden

    form = TaskForm(obj=task) 
    if form.validate_on_submit():
        try:
            task.description = form.description.data
            task.due_date = form.due_date.data
            task.priority = form.priority.data
            task.status = form.status.data
            _update_task_reminder(task) # Add/Update reminder logic
            db.session.commit()
            flash('Tarefa atualizada com sucesso!', 'success')
            return redirect(url_for('todo.list_tasks'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar tarefa: {e}', 'danger')
    return render_template('todo/task_form.html', title='Edit Task', form=form, legend=f'Edit Task "{task.description[:30]}..."', task_id=task.id)
