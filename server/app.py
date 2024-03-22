from flask import Flask, render_template
from users import users_bp
from workers import workers_bp
from domain import domains_bp
from location import locations_bp
from request import requests_bp
from database import db

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/', methods=['GET'])
def home():
    return render_template("home/home.html")

app.register_blueprint(users_bp)
app.register_blueprint(workers_bp)
app.register_blueprint(domains_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(requests_bp)

db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
