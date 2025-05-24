from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_ # For search queries
from .forms import QuickNoteForm
from .models import QuickNote # Ensure QuickNote is imported
from . import db
from datetime import datetime

note_bp = Blueprint('note', __name__)

@note_bp.route('/', methods=['GET']) # Default to list view, allow GET for search query
@login_required
def list_notes():
    """Displays the list of quick notes for the current user with search and filtering."""
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    notes_query = QuickNote.query.filter_by(user_id=current_user.id)

    if search_term:
        # Case-insensitive search in content and category
        notes_query = notes_query.filter(
            or_(
                QuickNote.content.ilike(f'%{search_term}%'),
                QuickNote.category.ilike(f'%{search_term}%') 
            )
        )
    
    if category_filter:
        notes_query = notes_query.filter(QuickNote.category.ilike(f'%{category_filter}%'))

    # Get distinct categories for the filter dropdown
    # This query gets a list of tuples, so we extract the first element of each tuple.
    # We only consider categories from the current user's notes.
    user_categories_query = db.session.query(QuickNote.category)\
        .filter(QuickNote.user_id == current_user.id, QuickNote.category != None, QuickNote.category != '')\
        .distinct().order_by(QuickNote.category)
    
    available_categories = [cat[0] for cat in user_categories_query.all()]

    notes_pagination = notes_query.order_by(QuickNote.updated_at.desc())\
                                  .paginate(page=page, per_page=10) # Simple pagination
    
    return render_template('notes/note_list.html', 
                           title='My Quick Notes', 
                           notes_pagination=notes_pagination,
                           search_term=search_term,
                           category_filter=category_filter,
                           available_categories=available_categories)

@note_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_note():
    """Handles adding a new quick note."""
    form = QuickNoteForm()
    if form.validate_on_submit():
        try:
            new_note = QuickNote(
                user_id=current_user.id,
                content=form.content.data,
                category=form.category.data.strip() if form.category.data else None
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Quick note created successfully!', 'success')
            return redirect(url_for('note.list_notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quick note: {e}', 'danger')
    return render_template('notes/note_form.html', title='Add Quick Note', form=form, legend='New Quick Note')

@note_bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    """Handles editing an existing quick note."""
    note = QuickNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403) # Forbidden

    form = QuickNoteForm(obj=note) # Pre-populate form
    if form.validate_on_submit():
        try:
            note.content = form.content.data
            note.category = form.category.data.strip() if form.category.data else None
            note.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Quick note updated successfully!', 'success')
            return redirect(url_for('note.list_notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating quick note: {e}', 'danger')
    return render_template('notes/note_form.html', title='Edit Quick Note', form=form, legend=f'Edit Note', note_id=note.id)

@note_bp.route('/delete/<int:note_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_note(note_id):
    """Handles deleting a quick note."""
    note = QuickNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Quick note deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quick note: {e}', 'danger')
    
    return redirect(url_for('note.list_notes'))
