from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from database import db
import imghdr
import io
from flask import send_file
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from sqlalchemy.sql import text

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
    subject = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    admin_comments = db.Column(db.String(200), nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

@requests_bp.route("/requests", methods=['GET', 'POST'])
@login_required
def home(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    print(user_type)
    if user_type != 'admin':
        return render_template("home/notfound.html")
    status_filter = request.args.get('status')

    if status_filter:
        if status_filter == 'pending':
            query = text("""
                SELECT r.request_id as request_id, r.user_id as user_id, r.domain_id as domain_id, r.location_id as location_id, r.subject as subject, 
                    r.availability as availability, r.status as status, r.description as description, r.admin_comments as admin_comments, 
                    r.image as image, r.created_at as created_at,
                    u.First_Name as first_name, u.Last_Name as last_name, u.Email_Id as email_id, u.mobile_number as mobile_number
                FROM Request_Table r
                JOIN User_Table u ON r.user_id = u.User_Id
                WHERE r.status = 'Pending'
            """)
        elif status_filter == 'ongoing':
            query = text("""
                SELECT r.request_id as request_id, r.user_id as user_id, r.domain_id as domain_id, r.location_id as location_id, r.subject as subject, 
                    r.availability as availability, r.status as status, r.description as description, r.admin_comments as admin_comments, 
                    r.image as image, r.created_at as created_at,
                    u.First_Name as first_name, u.Last_Name as last_name, u.Email_Id as email_id, u.mobile_number as mobile_number
                FROM Request_Table r
                JOIN User_Table u ON r.user_id = u.User_Id
                WHERE r.status = 'Ongoing'
            """)
        elif status_filter == 'completed':
            query = text("""
                SELECT r.request_id as request_id, r.user_id as user_id, r.domain_id as domain_id, r.location_id as location_id, r.subject as subject, 
                    r.availability as availability, r.status as status, r.description as description, r.admin_comments as admin_comments, 
                    r.image as image, r.created_at as created_at,
                    u.First_Name as first_name, u.Last_Name as last_name, u.Email_Id as email_id, u.mobile_number as mobile_number
                FROM Request_Table r
                JOIN User_Table u ON r.user_id = u.User_Id
                WHERE r.status = 'Completed'
            """)
        else:
            query = text("""
                SELECT r.request_id as request_id, r.user_id as user_id, r.domain_id as domain_id, r.location_id as location_id, r.subject as subject, 
                    r.availability as availability, r.status as status, r.description as description, r.admin_comments as admin_comments, 
                    r.image as image, r.created_at as created_at,
                    u.First_Name as first_name, u.Last_Name as last_name, u.Email_Id as email_id, u.mobile_number as mobile_number
                FROM Request_Table r
                JOIN User_Table u ON r.user_id = u.User_Id
            """)
    else:
        query = text("""
                SELECT r.request_id as request_id, r.user_id as user_id, r.domain_id as domain_id, r.location_id as location_id, r.subject as subject, 
                    r.availability as availability, r.status as status, r.description as description, r.admin_comments as admin_comments, 
                    r.image as image, r.created_at as created_at,
                    u.First_Name as first_name, u.Last_Name as last_name, u.Email_Id as email_id, u.mobile_number as mobile_number
                FROM Request_Table r
                JOIN User_Table u ON r.user_id = u.User_Id
            """)

    filtered_requests = db.session.execute(query).fetchall()
    today = datetime.utcnow().date()
    ten_days_ago = today - timedelta(days=10)
    pending_count = db.session.query(func.count(Requests.request_id)).filter(Requests.status == 'Pending', Requests.created_at >= ten_days_ago).scalar()
    ongoing_count = db.session.query(func.count(Requests.request_id)).filter(Requests.status == 'Ongoing', Requests.created_at >= ten_days_ago).scalar()
    completed_count = db.session.query(func.count(Requests.request_id)).filter(Requests.status == 'Completed', Requests.created_at >= ten_days_ago).scalar()
    return render_template("requests/home.html", details=filtered_requests, message=message, pending_count=pending_count, ongoing_count=ongoing_count, completed_count=completed_count, status_filter=status_filter)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@requests_bp.route("/requests/add", methods=['GET', 'POST'])
def add_requests(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    if request.method == 'POST':
        user_id = request.form['user_id']
        domain_id = request.form['domain_id']
        location_id = request.form['location_id']
        subject = request.form['subject']
        availability = request.form['availability']
        status = request.form['status']
        description = request.form['description']
        admin_comments = request.form['admin_comments']
        image = request.files['image']
        if image and allowed_file(image.filename):
            image_data = image.read()
        else:
            image_data = None
        try:
            new_request = Requests(user_id=user_id, domain_id=domain_id, location_id=location_id, subject=subject, availability=availability, status=status, description=description, admin_comments=admin_comments, image=image_data)
            db.session.add(new_request)
            db.session.commit()
            message = "Request added successfully"
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the Request. Please check if the any of the foreign keys (user_id, domain_id, location_id) are invalid."
        return render_template("requests/requests.html", message=message)
    return render_template("requests/requests.html", message=message)

@requests_bp.route("/requests/update/<int:request_id>", methods=['GET', 'POST'])
@login_required
def update_request(request_id, message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    requests = Requests.query.get_or_404(request_id)
    if request.method == 'POST':
        user_id = request.form['user_id'] 
        domain_id = request.form['domain_id']
        location_id = request.form['location_id']
        subject = request.form['subject']
        availability = request.form['availability']
        status = request.form['status']
        description = request.form['description']
        admin_comments = request.form['admin_comments']
        image = request.files['image']
        if image and allowed_file(image.filename):
            image_data = image.read()
        else:
            image_data = None
        try:
            Requests.query.filter_by(request_id=request_id).update(dict(user_id=user_id, domain_id=domain_id, location_id=location_id, subject=subject, availability=availability, status=status, description=description, admin_comments=admin_comments, image=image_data))
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
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
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


@requests_bp.route('/requests/image/<int:request_id>')
def serve_image(request_id):
    request_entry = Requests.query.get_or_404(request_id)
    if request_entry.image:
        image_data = io.BytesIO(request_entry.image)
        image_type = imghdr.what(None, h=request_entry.image)
        if image_type is None:
            return 'No image', 404
        image_data.seek(0)  # Seek to the start of the StringIO object before sending it
        mimetype = 'image/' + image_type
        return send_file(
            image_data,
            mimetype=mimetype,
            as_attachment=False,
            download_name=f'request_{request_id}.{image_type}'
        )
    else:
        return 'No image', 404
