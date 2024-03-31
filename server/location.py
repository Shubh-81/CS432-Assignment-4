from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required
from database import db

locations_bp = Blueprint('locations', __name__)

table_name = 'location_table'

class Locations(db.Model):
    __tablename__ = "location_table"
 
    location_id = db.Column(db.Integer, primary_key=True, unique=True)
    location = db.Column(db.String(500), nullable=False)
    building_name = db.Column(db.String(500), nullable=False)
    room_no = db.Column(db.String(500), nullable=True)
    description = db.Column(db.String(500), nullable=True)


@locations_bp.route("/locations", methods=['GET', 'POST'])
@login_required
def home(message=None):
    details = Locations.query.all()
    return render_template("locations/home.html", details=details, message=message)
 
@locations_bp.route("/locations/add", methods=['GET', 'POST'])
@login_required
def add_locations(message=None):
    if request.method == 'POST':
        location = request.form['location']
        building_name = request.form['building_name']
        room_no = request.form['room_no']
        description = request.form['description']
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (location, building_name, room_no, description) VALUES ('{location}', '{building_name}', '{room_no}', '{description}')"))
            db.session.commit()
            db.session.close()
            message = "Location added successfully"
            return render_template("locations/locations.html", message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the location. Please check your input."
            return render_template("locations/locations.html", message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])
 
    return render_template("locations/locations.html", message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])

@locations_bp.route("/locations/update/<int:location_id>", methods=['GET', 'POST'])
@login_required
def update_location(location_id, message=None):
    try:
        location = Locations.query.get_or_404(location_id)
        if request.method == 'POST':
            location = request.form['location']
            building_name = request.form['building_name']
            room_no = request.form['room_no']
            description = request.form['description']
            try:
                db.session.execute(text(f"UPDATE {table_name} SET location = '{location}', building_name = '{building_name}', room_no = '{room_no}', description = '{description}' WHERE location_id = {location_id}"))
                db.session.commit()
                db.session.close()
                message = "Location updated successfully"
                location = Locations.query.get_or_404(location_id)
                return render_template("locations/update_location.html", location=location, message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])
            except Exception as e:
                db.session.rollback() 
                print(e)
                message = "An error occurred while updating the location. Please check if the email id or mobile number is already in use."
                return render_template("locations/update_location.html", location=location, message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])
        
        return render_template("locations/update_location.html", location=location, message=message, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'])
    except Exception as e:
        print(e)
        message = "An error occurred while updating the location. Please check your input."
        return render_template("locations/update_location.html", location=location, message=message)

@locations_bp.route("/locations/delete/<int:location_id>", methods=['POST'])
@login_required
def delete_location(location_id):
    if request.method == 'POST':
        try:
            db.session.execute(text(f"DELETE FROM {table_name} WHERE location_id = {location_id}"))
            db.session.commit()
            db.session.close()
            message = "Location deleted successfully"
            return render_template("locations/home.html", details=Locations.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("locations/home.html", details=Locations.query.all(), message=message)
        
