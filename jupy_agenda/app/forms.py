from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User # To check for existing username/email

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Validate that the username is not already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        """Validate that the email is not already taken."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address is already registered. Please use a different one or login.')

class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me') # For "remember me" functionality
    submit = SubmitField('Login')

from wtforms import TextAreaField, DateTimeField
from wtforms.validators import Optional

class EventForm(FlaskForm):
    """Form for creating or editing an event."""
    title = StringField('Title', 
                        validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', 
                                validators=[Optional(), Length(max=500)]) # Optional field
    start_time = DateTimeField('Start Time (YYYY-MM-DD HH:MM:SS)', 
                               validators=[DataRequired()], 
                               format='%Y-%m-%d %H:%M:%S')
    end_time = DateTimeField('End Time (YYYY-MM-DD HH:MM:SS)', 
                             validators=[DataRequired()], 
                             format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Save Event')

    def validate_end_time(self, end_time_field):
        """Ensure end_time is after start_time."""
        if self.start_time.data and end_time_field.data:
            if end_time_field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time.')

from wtforms import DateField, SelectField

class TaskForm(FlaskForm):
    """Form for creating or editing a task."""
    description = TextAreaField('Description', 
                                validators=[DataRequired(), Length(min=1, max=1000)])
    due_date = DateField('Due Date (YYYY-MM-DD)', 
                         validators=[Optional()], 
                         format='%Y-%m-%d')
    priority = SelectField('Priority', 
                           choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')], 
                           coerce=int,
                           validators=[DataRequired()])
    status = SelectField('Status', 
                         choices=[('pending', 'Pending'), ('completed', 'Completed')], 
                         validators=[DataRequired()])
    submit = SubmitField('Save Task')

from wtforms import FloatField
from wtforms.validators import NumberRange

class LocationForm(FlaskForm):
    """Form for creating or editing a location."""
    name = StringField('Name', 
                       validators=[DataRequired(), Length(max=120)])
    address = TextAreaField('Address', 
                            validators=[Optional(), Length(max=500)])
    description = TextAreaField('Description', 
                                validators=[Optional(), Length(max=1000)])
    latitude = FloatField('Latitude', 
                          validators=[Optional(), NumberRange(min=-90.0, max=90.0, message="Latitude must be between -90 and 90.")])
    longitude = FloatField('Longitude', 
                           validators=[Optional(), NumberRange(min=-180.0, max=180.0, message="Longitude must be between -180 and 180.")])
    submit = SubmitField('Save Location')

class DiagramNoteForm(FlaskForm):
    """Form for creating or editing a diagram note."""
    title = StringField('Title', 
                        validators=[DataRequired(), Length(max=150)])
    content = TextAreaField('Content (Text-based diagram, notes, etc.)', 
                            validators=[Optional(), Length(max=10000)]) # Max length for content
    submit = SubmitField('Save Diagram Note')

class CodeSnippetForm(FlaskForm):
    """Form for creating or editing a code snippet."""
    title = StringField('Title', 
                        validators=[DataRequired(), Length(max=150)])
    content = TextAreaField('Code Snippet / Pseudocode', 
                            validators=[DataRequired(), Length(max=20000)]) # Max length for content
    language_hint = StringField('Language (e.g., python, javascript, pseudocode)', 
                                validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save Code Snippet')

from flask_wtf.file import FileField, FileAllowed, FileRequired

class LearningMaterialForm(FlaskForm):
    """Form for uploading or editing learning materials."""
    title = StringField('Title', 
                        validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', 
                                validators=[Optional(), Length(max=2000)])
    subject_category = StringField('Subject/Category', 
                                   validators=[Optional(), Length(max=100)])
    upload_date = DateField('Upload Date (YYYY-MM-DD)', 
                            format='%Y-%m-%d',
                            validators=[Optional()]) # Default is handled by model
    file = FileField('File', 
                     validators=[
                         # FileRequired() # Use only on creation, not edit unless replacing
                     ]) # Add FileAllowed later if needed for specific file types

    # Submit button for the form
    submit = SubmitField('Save Material')

class EditLearningMaterialForm(FlaskForm):
    """Form for editing learning materials (file field is optional)."""
    title = StringField('Title', 
                        validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', 
                                validators=[Optional(), Length(max=2000)])
    subject_category = StringField('Subject/Category', 
                                   validators=[Optional(), Length(max=100)])
    upload_date = DateField('Upload Date (YYYY-MM-DD)', 
                            format='%Y-%m-%d',
                            validators=[Optional()])
    # File field is intentionally omitted or made optional for editing details without re-uploading
    # If you want to allow file replacement, add it here with FileAllowed but not FileRequired
    file = FileField('Replace File (Optional)', 
                     validators=[
                         Optional(),
                         FileAllowed(['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'ppt', 'pptx', 'xls', 'xlsx', 'md'], 
                                     'Allowed file types: pdf, doc(x), txt, jpg, png, ppt(x), xls(x), md')
                     ])
    submit = SubmitField('Update Material')

class QuickNoteForm(FlaskForm):
    """Form for creating or editing a quick note."""
    content = TextAreaField('Note Content', 
                            validators=[DataRequired(), Length(min=1, max=5000)])
    category = StringField('Category (Optional)', 
                           validators=[Optional(), Length(max=100)])
    submit = SubmitField('Save Note')
