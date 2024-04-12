from sqlalchemy.sql import text
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from database import db
from auth import Users

users_bp = Blueprint('users', __name__)

table_name = 'user_table'


@users_bp.route("/users", methods=['GET', 'POST'])
@login_required
def home(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    user_filter = request.args.get('user_type')
    details = Users.query.all()
    if user_filter:
        if user_filter == 'user':
            filtered_requests = Users.query.filter_by(type='user').all()
        elif user_filter == 'admin':
            filtered_requests = Users.query.filter_by(type='admin').all()
        else:
            filtered_requests = details
    else:
        filtered_requests = details
    return render_template("users/home.html", details=filtered_requests, message=message, user_filter=user_filter)
 
@users_bp.route("/users/add", methods=['GET', 'POST'])
@login_required
def add_users(message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        user_type = request.form['type']
        if not user_type:
            user_type = 'user'
        try:
            db.session.execute(text(f"INSERT INTO {table_name} (first_name, last_name, email_id, mobile_number, user_type) VALUES ('{first_name}', '{last_name}', '{email_id}', '{mobile_number}', '{user_type}')"))
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
@login_required
def update_user(user_id, message=None):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
    user = Users.query.get_or_404(user_id)
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        user_type = request.form['type']
        if not user_type:
            user_type = 'user'
        try:
            db.session.execute(text(f"UPDATE {table_name} SET first_name = '{first_name}', last_name = '{last_name}', email_id = '{email_id}', mobile_number = '{mobile_number}', type = '{user_type}' WHERE user_id = {user_id}"))
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
@login_required
def delete_user(user_id):
    user_type = db.session.execute(text(f"SELECT type FROM user_table WHERE user_id = {current_user.user_id}")).fetchone()
    user_type = user_type[0]
    if user_type != 'admin':
        return render_template("home/notfound.html")
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
        
