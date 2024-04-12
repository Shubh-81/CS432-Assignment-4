from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from database import db

workers_bp = Blueprint('workers', __name__)

table_name = 'worker_table'

class Workers(db.Model):
    __tablename__ = "worker_table"
 
    worker_id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=True)
    domain_id = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    mobile_number = db.Column(db.String(10), nullable=False, unique=True)


@workers_bp.route("/workers", methods=['GET', 'POST'])
@login_required
def home(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    details = Workers.query.all()
    return render_template("workers/home.html", details=details, message=message)
 
@workers_bp.route("/workers/add", methods=['GET', 'POST'])
@login_required
def add_workers(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        domain_id = request.form['domain_id']
        availability = request.form['availability']
        mobile_number = request.form['mobile_number']
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (first_name, last_name, domain_id, availability, mobile_number) VALUES ('{first_name}', '{last_name}', '{domain_id}', '{availability}', '{mobile_number}')"))
            db.session.commit()
            db.session.close()
            message = "Worker added successfully"
            return render_template("workers/workers.html", message=message)
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the worker. Please check if the mobile number is already in use."
            return render_template("workers/workers.html", message=message)
 
    return render_template("workers/workers.html", message=message)

@workers_bp.route("/workers/update/<int:worker_id>", methods=['GET', 'POST'])
@login_required
def update_worker(worker_id, message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    worker = Workers.query.get_or_404(worker_id)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        domain_id = request.form['domain_id']
        availability = request.form['availability']
        mobile_number = request.form['mobile_number']
        try:
            db.session.execute(text(f"UPDATE {table_name} SET first_name = '{first_name}', last_name = '{last_name}', domain_id = '{domain_id}', mobile_number = '{mobile_number}', availability = '{availability}' WHERE worker_id = {worker_id}"))
            db.session.commit()
            db.session.close()
            message = "Worker updated successfully"
            worker = Workers.query.get_or_404(worker_id)
            return render_template("workers/update_worker.html", worker=worker, message=message)
        except Exception as e:
            db.session.rollback() 
            print(e)
            message = "An error occurred while updating the worker. Please check if the email id or mobile number is already in use."
            return render_template("workers/update_worker.html", worker=worker, message=message)
    
    return render_template("workers/update_worker.html", worker=worker, message=message)

@workers_bp.route("/workers/delete/<int:worker_id>", methods=['POST'])
@login_required
def delete_worker(worker_id):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    if request.method == 'POST':
        try:
            db.session.execute(text(f"DELETE FROM {table_name} WHERE worker_id = {worker_id}"))
            db.session.commit()
            db.session.close()
            message = "Worker deleted successfully"
            return render_template("workers/home.html", details=Workers.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("workers/home.html", details=Workers.query.all(), message=message)
        
