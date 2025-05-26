from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Serves the homepage."""
    # The existing index.html can be used or a new one created.
    # For now, it refers to the one created in the previous subtask.
    return render_template('index.html', title='Home')

@main_bp.route('/profile')
@login_required # Ensure only logged-in users can see this
def profile():
    """Serves the user profile page."""
    # You can pass user-specific data to the template if needed
    return render_template('profile.html', title='Profile', user=current_user)
