from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from users import users_bp
from workers import workers_bp
from domain import domains_bp
from location import locations_bp
from request import requests_bp
from auth import auth, Users
from database import db
from flask_login import login_user, logout_user, login_required
from sqlalchemy.sql import text
from request import Requests


app = Flask(__name__)
app.config.from_pyfile('config.py')

UPLOAD_FOLDER = 'uploads'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type == 'admin':
        return render_template("home/home.html")
    else:
        if request.method == 'POST':
            domains = db.session.execute(text(f"SELECT * FROM domain_table")).fetchall()
            user_id = current_user.user_id
            domain = request.form['domain']
            subdomain = request.form['subdomain']
            subdomain_2 = request.form['subdomain2']
            domain_id = db.session.execute(text(f"SELECT domain_id FROM domain_table WHERE domain = '{domain}' AND subdomain = '{subdomain}' AND subdomain_2 = '{subdomain_2}'")).fetchone()
            if not domain_id:
                message = "An error occurred while adding the domain. Please check your input."
                return render_template("home/userrequest.html", message=message, user_id=current_user.user_id, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'], domains=domains)
            domain_id = domain_id[0]
            location = request.form['location']
            building_name = request.form['building_name']
            room_number = request.form['room_no']
            location_description = request.form['location_description']
            location_id = db.session.execute(text(f"SELECT location_id FROM location_table WHERE location = '{location}' AND building_name = '{building_name}' AND room_no = '{room_number}' AND description = '{location_description}'")).fetchone()
            if not location_id:
                try:
                    db.session.execute(text(f"INSERT INTO location_table (location, building_name, room_no, description) VALUES ('{location}', '{building_name}', '{room_number}', '{location_description}')"))
                    db.session.commit()
                    location_id = db.session.execute(text(f"SELECT location_id FROM location_table WHERE location = '{location}' AND building_name = '{building_name}' AND room_no = '{room_number}' AND description = '{location_description}'")).fetchone()
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    message = "An error occurred while adding the location. Please check your input."
                    return render_template("home/userrequest.html", message=message, user_id=current_user.user_id, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'], domains=domains)
            location_id = location_id[0]
            subject = request.form['subject']
            availability = request.form['availability']
            status = 'pending'
            description = request.form['description']
            admin_comments = ''
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
            return render_template("home/userrequest.html", message=message, user_id=current_user.user_id, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'], domains=domains)
        domains = db.session.execute(text(f"SELECT * FROM domain_table")).fetchall()
        return render_template("home/userrequest.html", user_id=current_user.user_id, locations=['Hostel','Housing','Academic','Infrastructure','Guest House','Central Arcade','Sports Complex','Research Park'], domains=domains)

@app.route('/userrequests', methods=['GET'])
@login_required
def userrequests():
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type == 'admin':
        return render_template("home/notfound.html")
    user_id = current_user.user_id
    requests = db.session.execute(text(f"SELECT * FROM request_table WHERE user_id = {user_id}")).fetchall()
    print(requests)
    return render_template("home/user_requests.html", details=requests)

@app.route('/<path:path>')
def catch_all(path):
    return render_template('home/notfound.html'), 404

app.register_blueprint(users_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(domains_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(auth)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users(user_id=user_id)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
