from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .forms import LocationForm
from .models import Location # Ensure Location is imported
from . import db
from datetime import datetime

location_bp = Blueprint('location', __name__)

@location_bp.route('/') # Default to list view
@login_required
def list_locations():
    """Displays the list of locations for the current user."""
    page = request.args.get('page', 1, type=int)
    locations_pagination = Location.query.filter_by(user_id=current_user.id)\
                                       .order_by(Location.created_at.desc())\
                                       .paginate(page=page, per_page=10) # Simple pagination
    
    return render_template('locations/location_list.html', 
                           title='My Locations', 
                           locations_pagination=locations_pagination)

@location_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_location():
    """Handles adding a new location."""
    form = LocationForm()
    if form.validate_on_submit():
        try:
            new_location = Location(
                user_id=current_user.id,
                name=form.name.data,
                address=form.address.data,
                description=form.description.data,
                latitude=form.latitude.data,
                longitude=form.longitude.data
            )
            db.session.add(new_location)
            db.session.commit()
            flash('Location created successfully!', 'success')
            return redirect(url_for('location.list_locations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating location: {e}', 'danger')
            # app.logger.error(f"Error creating location: {e}") # For server-side logging
    return render_template('locations/location_form.html', title='Add Location', form=form, legend='New Location')

@location_bp.route('/edit/<int:location_id>', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    """Handles editing an existing location."""
    location = Location.query.get_or_404(location_id)
    if location.user_id != current_user.id:
        abort(403) # Forbidden

    form = LocationForm(obj=location) # Pre-populate form with location data
    if form.validate_on_submit():
        try:
            location.name = form.name.data
            location.address = form.address.data
            location.description = form.description.data
            location.latitude = form.latitude.data
            location.longitude = form.longitude.data
            location.updated_at = datetime.utcnow() # Manually update if not using onupdate in model for all changes
            db.session.commit()
            flash('Location updated successfully!', 'success')
            return redirect(url_for('location.list_locations'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating location: {e}', 'danger')
    return render_template('locations/location_form.html', title='Edit Location', form=form, legend=f'Edit "{location.name}"', location_id=location.id)

@location_bp.route('/delete/<int:location_id>', methods=['POST']) # POST only for deletion
@login_required
def delete_location(location_id):
    """Handles deleting a location."""
    location = Location.query.get_or_404(location_id)
    if location.user_id != current_user.id:
        abort(403) # Forbidden
    
    try:
        db.session.delete(location)
        db.session.commit()
        flash('Location deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting location: {e}', 'danger')
    
    return redirect(url_for('location.list_locations'))

# Optional: Detail View (if not using edit page for viewing details)
@location_bp.route('/view/<int:location_id>')
@login_required
def view_location(location_id):
    """Displays details of a specific location."""
    location = Location.query.get_or_404(location_id)
    if location.user_id != current_user.id:
        abort(403) # Forbidden
    # If you create a location_detail.html, use it here
    # For now, could redirect to edit view or just display info on a simple page
    return render_template('locations/location_detail.html', title=f"Location: {location.name}", location=location)
