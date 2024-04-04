from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required
from database import db
import imghdr
import io
from flask import send_file
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@requests_bp.route("/requests/add", methods=['GET', 'POST'])
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
