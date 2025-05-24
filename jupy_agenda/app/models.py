from . import db  # Import db instance from app/__init__.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'  # Optional: specify table name

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False) # Increased length for potentially longer hashes

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

from datetime import datetime

class Event(db.Model):
    """Event model for calendar entries."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User (optional, but good for ORM access)
    user = db.relationship('User', backref=db.backref('events', lazy=True))

    def __repr__(self):
        return f'<Event {self.title} (User: {self.user_id})>'

    # You might add methods here, e.g., to check duration, or if an event is ongoing.

# Make sure datetime is imported if not already at the top
# from datetime import datetime # Already imported for Event model

class Task(db.Model):
    """Task model for To-Do list items."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=True) # Date field for due date
    priority = db.Column(db.Integer, default=1, nullable=False) # 1-Low, 2-Medium, 3-High
    status = db.Column(db.String(20), default='pending', nullable=False, index=True) # e.g., 'pending', 'completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic')) # lazy='dynamic' for querying

    def __repr__(self):
        return f'<Task {self.id}: {self.description[:30]}... (User: {self.user_id}, Status: {self.status})>'

    # Helper for priority display (optional)
    @property
    def priority_display(self):
        priorities = {1: 'Low', 2: 'Medium', 3: 'High'}
        return priorities.get(self.priority, 'Unknown')

# Ensure datetime is available (already imported for Event and Task)
# from datetime import datetime

class Location(db.Model):
    """Location model for storing user-defined places."""
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # For tracking updates

    # Relationship to User
    user = db.relationship('User', backref=db.backref('locations', lazy='dynamic'))

    def __repr__(self):
        return f'<Location {self.id}: {self.name} (User: {self.user_id})>'

# Ensure datetime is available (already imported)
# from datetime import datetime

class DiagramNote(db.Model):
    """Model for text-based diagram notes."""
    __tablename__ = 'diagram_notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('diagram_notes', lazy='dynamic'))

    def __repr__(self):
        return f'<DiagramNote {self.id}: {self.title} (User: {self.user_id})>'

# Ensure datetime is available (already imported)
# from datetime import datetime

class CodeSnippet(db.Model):
    """Model for code snippets."""
    __tablename__ = 'code_snippets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language_hint = db.Column(db.String(50), nullable=True) # e.g., 'python', 'javascript', 'pseudocode'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('code_snippets', lazy='dynamic'))

    def __repr__(self):
        return f'<CodeSnippet {self.id}: {self.title} (User: {self.user_id}, Lang: {self.language_hint})>'

# Ensure datetime is available (already imported)
# from datetime import datetime

class Reminder(db.Model):
    """Model for storing reminders for events or tasks."""
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # 'event' or 'task'
    item_id = db.Column(db.Integer, nullable=False) # ID of the Event or Task
    reminder_time = db.Column(db.DateTime, nullable=False)
    notification_method = db.Column(db.String(20), default='email', nullable=False)
    sent_status = db.Column(db.String(20), default='pending', nullable=False) # 'pending', 'sent', 'error'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('reminders', lazy='dynamic'))

    __table_args__ = (db.Index('ix_reminder_time_sent_status', 'reminder_time', 'sent_status'),)

    def __repr__(self):
        return f'<Reminder {self.id} for {self.item_type} {self.item_id} at {self.reminder_time} (Status: {self.sent_status})>'

# Ensure datetime and date are available
from datetime import date # For default upload_date

class LearningMaterial(db.Model):
    """Model for learning materials (uploaded files)."""
    __tablename__ = 'learning_materials'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_name = db.Column(db.String(255), nullable=False)  # Original name of the uploaded file
    file_path = db.Column(db.String(512), nullable=False, unique=True) # Unique path/name on the server
    subject_category = db.Column(db.String(100), nullable=True)
    upload_date = db.Column(db.Date, default=date.today) # Default to current date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to User
    user = db.relationship('User', backref=db.backref('learning_materials', lazy='dynamic'))

    def __repr__(self):
        return f'<LearningMaterial {self.id}: {self.title} (User: {self.user_id})>'
