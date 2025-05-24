from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .forms import DiagramNoteForm
from .models import DiagramNote # Ensure DiagramNote is imported
from . import db
from datetime import datetime

diagram_bp = Blueprint('diagram', __name__)

@diagram_bp.route('/') # Default to list view
@login_required
def list_diagram_notes():
    """Displays the list of diagram notes for the current user."""
    page = request.args.get('page', 1, type=int)
    notes_pagination = DiagramNote.query.filter_by(user_id=current_user.id)\
                                      .order_by(DiagramNote.updated_at.desc())\
                                      .paginate(page=page, per_page=10) # Simple pagination
    
    return render_template('diagrams/diagram_list.html', 
                           title='My Diagram Notes', 
                           notes_pagination=notes_pagination)

@diagram_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_diagram_note():
    """Handles adding a new diagram note."""
    form = DiagramNoteForm()
    if form.validate_on_submit():
        try:
            new_note = DiagramNote(
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data
            )
            db.session.add(new_note)
            db.session.commit()
            flash('Nota de diagrama criada com sucesso!', 'success')
            return redirect(url_for('diagram.list_diagram_notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar nota de diagrama: {e}', 'danger')
    return render_template('diagrams/diagram_form.html', title='Add Diagram Note', form=form, legend='New Diagram Note')

@diagram_bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_diagram_note(note_id):
    """Handles editing an existing diagram note."""
    note = DiagramNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403) # Forbidden

    form = DiagramNoteForm(obj=note) # Pre-populate form
    if form.validate_on_submit():
        try:
            note.title = form.title.data
            note.content = form.content.data
            note.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Nota de diagrama atualizada com sucesso!', 'success')
            return redirect(url_for('diagram.list_diagram_notes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar nota de diagrama: {e}', 'danger')
    return render_template('diagrams/diagram_form.html', title='Edit Diagram Note', form=form, legend=f'Edit "{note.title}"', note_id=note.id)

@diagram_bp.route('/delete/<int:note_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_diagram_note(note_id):
    """Handles deleting a diagram note."""
    note = DiagramNote.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Nota de diagrama excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir nota de diagrama: {e}', 'danger')
    
    return redirect(url_for('diagram.list_diagram_notes'))
