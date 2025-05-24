from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegistrationForm
from .models import User
from . import db # Import db from app/__init__.py

# Create a Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) # Assuming a 'main' blueprint for homepage

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Parabéns, você agora é um usuário registrado!', 'success')
            login_user(user) # Log in the user after registration
            return redirect(url_for('main.index')) # Or wherever you want to redirect after registration
        except Exception as e:
            db.session.rollback()
            flash(f'Erro durante o registro: {e}', 'danger')
            # Log the error for debugging
            # current_app.logger.error(f'Registration error: {e}')
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login bem-sucedido!', 'success')
            next_page = request.args.get('next') # For redirecting after login if 'next' is in URL
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Login malsucedido. Por favor, verifique seu email e senha', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required # Ensures only logged-in users can access this route
def logout():
    """Handles user logout."""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('auth.login'))

# It's good practice to have a placeholder for the main index route
# This will be properly defined later, perhaps in a main_routes.py
# For now, to avoid errors with url_for until main blueprint is created:
# You might need a dummy 'main.index' if you run this before main blueprint is ready.
# For example, create a dummy blueprint in __init__.py for now or in a new main_routes.py
# from flask import Blueprint, render_template
# main_bp_temp = Blueprint('main', __name__)
# @main_bp_temp.route('/')
# def index():
# return "Welcome!"
# app.register_blueprint(main_bp_temp)
# This is just a temporary measure for url_for calls.
# A proper main blueprint should be created.
