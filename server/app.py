from flask import Flask, render_template
from flask_login import LoginManager 
from users import users_bp
from workers import workers_bp
from domain import domains_bp
from location import locations_bp
from request import requests_bp
from auth import auth, User
from database import db
from flask_login import login_user, logout_user, login_required


app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home/home.html")

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
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
