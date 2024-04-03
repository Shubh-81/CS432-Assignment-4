from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required
from database import db
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 

requests_bp = Blueprint('requests', __name__)

table_name = 'Request_Table'

class Requests(db.Model):
    __tablename__ = "Request_Table"
 
    request_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, nullable=False)
    domain_id = db.Column(db.Integer, nullable=False)
    location_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    availability = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    admin_comments = db.Column(db.String(500), nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)


@requests_bp.route("/requests", methods=['GET', 'POST'])
@login_required
def home(message=None):
    details = Requests.query.all()
    return render_template("requests/home.html", details=details, message=message)
 
@requests_bp.route("/requests/add", methods=['GET', 'POST'])
@login_required
def add_requests(message=None):
    if request.method == 'POST':
        user_id = request.form['user_id']
        domain_id = request.form['domain_id']
        location_id = request.form['location_id']
        subject = request.form['subject']
        availability = request.form['availability']
        status = request.form['status']
        description = request.form['description']
        admin_comments = request.form['admin_comments']
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (user_id, domain_id, location_id, subject, availability, status, description, admin_comments) VALUES ('{user_id}', '{domain_id}', '{location_id}', '{subject}', '{availability}', '{status}', '{description}', '{admin_comments}')"))
            db.session.commit()
            db.session.close()
            message = "Request added successfully"
            return render_template("requests/requests.html", message=message)
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the Request. Please check if the any of the foreign keys (user_id, domain_id, location_id) are invalid."
            return render_template("requests/requests.html", message=message)
 
    return render_template("requests/requests.html", message=message)

@requests_bp.route("/requests/update/<int:request_id>", methods=['GET', 'POST'])
@login_required
def update_request(request_id, message=None):
    requests = Requests.query.get_or_404(request_id)
    print(requests)
    if request.method == 'POST':
        print(request.form)
        user_id = request.form['user_id'] 
        domain_id = request.form['domain_id']
        location_id = request.form['location_id']
        subject = request.form['subject']
        availability = request.form['availability']
        status = request.form['status']
        description = request.form['description']
        admin_comments = request.form['admin_comments']
        try:
            db.session.execute(text(f"UPDATE {table_name} SET user_id = '{user_id}', domain_id = '{domain_id}', location_id = '{location_id}', subject = '{subject}', availability = '{availability}', status = '{status}', description = '{description}', admin_comments = '{admin_comments}' WHERE request_id = {request_id}"))
            db.session.commit()
            db.session.close()
            message = "Request updated successfully"
            requests = Requests.query.get_or_404(request_id)
            return render_template("requests/update_request.html", requests=requests, message=message)
        except Exception as e:
            db.session.rollback() 
            print(e)
            message = "An error occurred while updating the Request. Please check if the any of the foreign keys (user_id, domain_id, location_id) are invalid."
            return render_template("requests/update_request.html", requests=requests, message=message)
    
    return render_template("requests/update_request.html", requests=requests, message=message)

@requests_bp.route("/requests/delete/<int:request_id>", methods=['POST'])
@login_required
def delete_request(request_id):
    if request.method == 'POST':
        try:
            db.session.execute(text(f"DELETE FROM {table_name} WHERE request_id = {request_id}"))
            db.session.commit()
            db.session.close()
            message = "Request deleted successfully"
            return render_template("requests/home.html", details=Requests.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("requests/home.html", details=Requests.query.all(), message=message)
        