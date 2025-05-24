import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import LearningMaterialForm, EditLearningMaterialForm # Import both forms
from .models import LearningMaterial
from . import db
from datetime import date, datetime

material_bp = Blueprint('material', __name__)

# Allowed extensions for file uploads (can be configured more centrally if needed)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'ppt', 'pptx', 'xls', 'xlsx', 'md'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@material_bp.route('/')
@login_required
def list_materials():
    """Displays the list of learning materials for the current user."""
    page = request.args.get('page', 1, type=int)
    materials_pagination = LearningMaterial.query.filter_by(user_id=current_user.id)\
                                             .order_by(LearningMaterial.upload_date.desc(), LearningMaterial.title.asc())\
                                             .paginate(page=page, per_page=10)
    return render_template('materials/material_list.html', 
                           title='My Learning Materials', 
                           materials_pagination=materials_pagination)

@material_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_material():
    """Handles uploading a new learning material."""
    form = LearningMaterialForm()
    # Add FileRequired and FileAllowed validators dynamically for the 'file' field on upload
    form.file.validators = [
        FileRequired(message="A file is required for upload."),
        FileAllowed(ALLOWED_EXTENSIONS, f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}')
    ]
    
    if form.validate_on_submit():
        file = form.file.data
        original_filename = secure_filename(file.filename)
        
        # Generate a unique filename using UUID and keep the original extension
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        
        # Construct the full path for saving the file
        # User-specific subdirectories could be current_user.username or current_user.id
        user_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
        if not os.path.exists(user_upload_folder):
            os.makedirs(user_upload_folder)
            
        file_server_path = os.path.join(user_upload_folder, unique_filename)
        
        try:
            file.save(file_server_path)
            
            new_material = LearningMaterial(
                user_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                file_name=original_filename, # Store original filename
                file_path=os.path.join(str(current_user.id), unique_filename), # Store relative path within UPLOAD_FOLDER
                subject_category=form.subject_category.data,
                upload_date=form.upload_date.data or date.today()
            )
            db.session.add(new_material)
            db.session.commit()
            flash('Learning material uploaded successfully!', 'success')
            return redirect(url_for('material.list_materials'))
        except Exception as e:
            db.session.rollback()
            # If file was saved but DB commit failed, attempt to delete the orphaned file
            if os.path.exists(file_server_path):
                try:
                    os.remove(file_server_path)
                except OSError as oe:
                    current_app.logger.error(f"Error deleting orphaned file {file_server_path} after DB error: {oe}")
            flash(f'Error uploading material: {e}', 'danger')
            current_app.logger.error(f"Error uploading material: {e}")
            
    return render_template('materials/material_form.html', title='Upload Material', form=form, legend='Upload New Material')

@material_bp.route('/download/<int:material_id>')
@login_required
def download_material(material_id):
    """Allows downloading a specific material."""
    material = LearningMaterial.query.get_or_404(material_id)
    if material.user_id != current_user.id:
        abort(403) # Forbidden
    
    # file_path is stored relative to UPLOAD_FOLDER/user_id/
    # So, the directory for send_from_directory is UPLOAD_FOLDER
    # and the filename is user_id/unique_filename (which is material.file_path)
    # This assumes material.file_path is like "user_id/uuid.ext"
    
    # Correct path construction:
    # The directory is current_app.config['UPLOAD_FOLDER']
    # The path_to_file is material.file_path (which should be 'user_id/unique_filename.ext')
    # This is because send_from_directory joins directory and path_to_file.
    
    # Example: UPLOAD_FOLDER = /instance/uploads/learning_materials
    # material.file_path = 1/some_uuid.pdf
    # send_from_directory will look for /instance/uploads/learning_materials/1/some_uuid.pdf
    
    try:
        return send_from_directory(
            directory=current_app.config['UPLOAD_FOLDER'], 
            path=material.file_path, # This is 'user_id/unique_filename.ext'
            as_attachment=True,
            download_name=material.file_name # Use original filename for download
        )
    except FileNotFoundError:
        current_app.logger.error(f"File not found for material ID {material_id}: Path {os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)}")
        abort(404)


@material_bp.route('/edit/<int:material_id>', methods=['GET', 'POST'])
@login_required
def edit_material(material_id):
    """Handles editing an existing learning material."""
    material = LearningMaterial.query.get_or_404(material_id)
    if material.user_id != current_user.id:
        abort(403)

    form = EditLearningMaterialForm(obj=material) # Use EditLearningMaterialForm
    
    if form.validate_on_submit():
        old_file_path_relative = material.file_path # e.g., "user_id/old_uuid.ext"
        old_file_server_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_file_path_relative)
        new_file_saved = False
        
        try:
            material.title = form.title.data
            material.description = form.description.data
            material.subject_category = form.subject_category.data
            material.upload_date = form.upload_date.data or material.upload_date # Keep old if not provided

            if form.file.data: # If a new file is uploaded
                file = form.file.data
                original_filename = secure_filename(file.filename)
                file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
                unique_filename = f"{uuid.uuid4()}.{file_ext}"
                
                user_upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
                if not os.path.exists(user_upload_folder): # Should exist, but double check
                    os.makedirs(user_upload_folder)
                
                new_file_server_path_temp = os.path.join(user_upload_folder, unique_filename)
                file.save(new_file_server_path_temp)
                new_file_saved = True

                material.file_name = original_filename
                material.file_path = os.path.join(str(current_user.id), unique_filename)
            
            material.updated_at = datetime.utcnow()
            db.session.commit()

            # If new file was uploaded and commit successful, delete old file
            if new_file_saved and old_file_path_relative != material.file_path: # Ensure it's a different file
                if os.path.exists(old_file_server_path):
                    try:
                        os.remove(old_file_server_path)
                    except OSError as oe:
                         current_app.logger.error(f"Error deleting old file {old_file_server_path} during edit: {oe}")
            
            flash('Learning material updated successfully!', 'success')
            return redirect(url_for('material.list_materials'))
        except Exception as e:
            db.session.rollback()
            # If new file was saved but DB commit failed, delete the newly uploaded temp file
            if new_file_saved and 'new_file_server_path_temp' in locals() and os.path.exists(new_file_server_path_temp):
                try:
                    os.remove(new_file_server_path_temp)
                except OSError as oe:
                    current_app.logger.error(f"Error deleting temp new file {new_file_server_path_temp} after DB error during edit: {oe}")

            flash(f'Error updating material: {e}', 'danger')
            current_app.logger.error(f"Error updating material: {e}")
            
    return render_template('materials/material_form.html', title='Edit Material', form=form, legend=f'Edit "{material.title}"', material_id=material.id, is_edit=True)


@material_bp.route('/delete/<int:material_id>', methods=['POST'])
@login_required
def delete_material(material_id):
    """Handles deleting a learning material."""
    material = LearningMaterial.query.get_or_404(material_id)
    if material.user_id != current_user.id:
        abort(403)

    file_server_path = os.path.join(current_app.config['UPLOAD_FOLDER'], material.file_path)
    
    try:
        db.session.delete(material)
        db.session.commit()
        
        # After successful DB deletion, delete the file
        if os.path.exists(file_server_path):
            try:
                os.remove(file_server_path)
                # Check if user-specific directory is empty and delete if so
                user_dir = os.path.dirname(file_server_path)
                if not os.listdir(user_dir): # Check if directory is empty
                    os.rmdir(user_dir)
            except OSError as e:
                flash(f'Error deleting file from server: {e}. Record deleted from DB.', 'warning')
                current_app.logger.error(f"Error deleting file {file_server_path}: {e}")
        else:
            flash('File not found on server, but record deleted from DB.', 'warning')
            current_app.logger.warning(f"File not found on server for deleted material: {file_server_path}")

        flash('Learning material deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting material: {e}', 'danger')
        current_app.logger.error(f"Error deleting material from DB: {e}")
        
    return redirect(url_for('material.list_materials'))
