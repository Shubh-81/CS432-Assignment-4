from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from database import db

users_bp = Blueprint('users', __name__)

table_name = 'user_table'

class Users(db.Model):
    __tablename__ = "user_table"
 
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(500), nullable=False)
    middle_name = db.Column(db.String(500), nullable=True)
    last_name = db.Column(db.String(500), nullable=True)
    email_id = db.Column(db.String(500), nullable=False, unique=True)
    mobile_number = db.Column(db.String(500), nullable=False, unique=True)


@users_bp.route("/users", methods=['GET', 'POST'])
def home(message=None):
    details = Users.query.all()
    return render_template("users/home.html", details=details, message=message)
 
@users_bp.route("/users/add", methods=['GET', 'POST'])
def add_users(message=None):
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (first_name, middle_name, last_name, email_id, mobile_number) VALUES ('{first_name}', '{middle_name}', '{last_name}', '{email_id}', '{mobile_number}')"))
            db.session.commit()
            db.session.close()
            message = "User added successfully"
            return render_template("users/users.html", message=message)
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the user. Please check if the email id or mobile number is already in use."
            return render_template("users/users.html", message=message)
 
    return render_template("users/users.html", message=message)

@users_bp.route("/users/update/<int:user_id>", methods=['GET', 'POST'])
def update_user(user_id, message=None):
    user = Users.query.get_or_404(user_id)
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        try:
            db.session.execute(text(f"UPDATE {table_name} SET first_name = '{first_name}', middle_name = '{middle_name}', last_name = '{last_name}', email_id = '{email_id}', mobile_number = '{mobile_number}' WHERE user_id = {user_id}"))
            db.session.commit()
            db.session.close()
            message = "User updated successfully"
            user = Users.query.get_or_404(user_id)
            return render_template("users/update_user.html", user=user, message=message)
        except Exception as e:
            db.session.rollback() 
            print(e)
            message = "An error occurred while updating the user. Please check if the email id or mobile number is already in use."
            return render_template("users/update_user.html", user=user, message=message)
    
    return render_template("users/update_user.html", user=user, message=message)

@users_bp.route("/users/delete/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    if request.method == 'POST':
        try:
            db.session.execute(text(f"DELETE FROM {table_name} WHERE user_id = {user_id}"))
            db.session.commit()
            db.session.close()
            message = "User deleted successfully"
            return render_template("users/home.html", details=Users.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("users/home.html", details=Users.query.all(), message=message)
        
