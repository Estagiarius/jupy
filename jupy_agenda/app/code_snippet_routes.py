from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .forms import CodeSnippetForm
from .models import CodeSnippet # Ensure CodeSnippet is imported
from . import db
from datetime import datetime

code_snippet_bp = Blueprint('code_snippet', __name__)

@code_snippet_bp.route('/') # Default to list view
@login_required
def list_code_snippets():
    """Displays the list of code snippets for the current user."""
    page = request.args.get('page', 1, type=int)
    snippets_pagination = CodeSnippet.query.filter_by(user_id=current_user.id)\
                                         .order_by(CodeSnippet.updated_at.desc())\
                                         .paginate(page=page, per_page=10) # Simple pagination
    
    return render_template('code_snippets/snippet_list.html', 
                           title='My Code Snippets', 
                           snippets_pagination=snippets_pagination)

@code_snippet_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_code_snippet():
    """Handles adding a new code snippet."""
    form = CodeSnippetForm()
    if form.validate_on_submit():
        try:
            new_snippet = CodeSnippet(
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data,
                language_hint=form.language_hint.data
            )
            db.session.add(new_snippet)
            db.session.commit()
            flash('Fragmento de código criado com sucesso!', 'success')
            return redirect(url_for('code_snippet.list_code_snippets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar fragmento de código: {e}', 'danger')
    return render_template('code_snippets/snippet_form.html', title='Add Code Snippet', form=form, legend='New Code Snippet')

@code_snippet_bp.route('/edit/<int:snippet_id>', methods=['GET', 'POST'])
@login_required
def edit_code_snippet(snippet_id):
    """Handles editing an existing code snippet."""
    snippet = CodeSnippet.query.get_or_404(snippet_id)
    if snippet.user_id != current_user.id:
        abort(403) # Forbidden

    form = CodeSnippetForm(obj=snippet) # Pre-populate form
    if form.validate_on_submit():
        try:
            snippet.title = form.title.data
            snippet.content = form.content.data
            snippet.language_hint = form.language_hint.data
            snippet.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Fragmento de código atualizado com sucesso!', 'success')
            return redirect(url_for('code_snippet.list_code_snippets'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar fragmento de código: {e}', 'danger')
    return render_template('code_snippets/snippet_form.html', title='Edit Code Snippet', form=form, legend=f'Edit "{snippet.title}"', snippet_id=snippet.id)

@code_snippet_bp.route('/delete/<int:snippet_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_code_snippet(snippet_id):
    """Handles deleting a code snippet."""
    snippet = CodeSnippet.query.get_or_404(snippet_id)
    if snippet.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        db.session.delete(snippet)
        db.session.commit()
        flash('Fragmento de código excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir fragmento de código: {e}', 'danger')
    
    return redirect(url_for('code_snippet.list_code_snippets'))

@code_snippet_bp.route('/view/<int:snippet_id>')
@login_required
def view_code_snippet(snippet_id):
    """Displays details of a specific code snippet (can be merged with edit or be separate)."""
    snippet = CodeSnippet.query.get_or_404(snippet_id)
    if snippet.user_id != current_user.id:
        abort(403)
    return render_template('code_snippets/snippet_view.html', title=f'View: {snippet.title}', snippet=snippet)
