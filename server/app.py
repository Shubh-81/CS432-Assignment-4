from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import yaml
 
app = Flask(__name__)

table_name = "user_table"

with open('db.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    host = config['mysql_host']
    db_name = config['mysql_db']
    db = SQLAlchemy()
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:12345678@{host}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

class Users(db.Model):
    __tablename__ = table_name
 
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(500), nullable=False)
    middle_name = db.Column(db.String(500), nullable=True)
    last_name = db.Column(db.String(500), nullable=True)
    email_id = db.Column(db.String(500), nullable=False, unique=True)
    mobile_number = db.Column(db.String(500), nullable=False, unique=True)


def create_db():
    with app.app_context():
        db.create_all()

@app.route("/users", methods=['GET', 'POST'])
def home(message=None):
    details = Users.query.all()
    return render_template("home.html", details=details, message=message)
 
@app.route("/users/add", methods=['GET', 'POST'])
def add_users(message=None):
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        db.session.execute(text(f"INSERT INTO {table_name} (first_name, middle_name, last_name, email_id, mobile_number) VALUES ('{first_name}', '{middle_name}', '{last_name}', '{email_id}', '{mobile_number}')"))
        try:
            db.session.commit()
            db.session.close()
            message = "User added successfully"
            return render_template("users.html", message=message)
        except Exception as e:
            db.session.rollback()
            print(e)
            message = "An error occurred while adding the user. Please check if the email id or mobile number is already in use."
            return render_template("users.html", message=message)
 
    return render_template("users.html", message=message)

@app.route("/users/update/<int:user_id>", methods=['GET', 'POST'])
def update_user(user_id, message=None):
    user = Users.query.get_or_404(user_id)
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        email_id = request.form['email_id']
        mobile_number = request.form['mobile_number']
        db.session.execute(text(f"UPDATE {table_name} SET first_name = '{first_name}', middle_name = '{middle_name}', last_name = '{last_name}', email_id = '{email_id}', mobile_number = '{mobile_number}' WHERE user_id = {user_id}"))
        try:
            db.session.commit()
            db.session.close()
            message = "User updated successfully"
            user = Users.query.get_or_404(user_id)
            return render_template("update_user.html", user=user, message=message)
        except Exception as e:
            db.session.rollback() 
            print(e)
            message = "An error occurred while updating the user. Please check if the email id or mobile number is already in use."
            return render_template("update_user.html", user=user, message=message)
    
    return render_template("update_user.html", user=user, message=message)

@app.route("/users/delete/<int:user_id>", methods=['POST'])
def delete_user(user_id):
    if request.method == 'POST':
        db.session.execute(text(f"DELETE FROM {table_name} WHERE user_id = {user_id}"))
        try:
            db.session.commit()
            db.session.close()
            message = "User deleted successfully"
            return render_template("home.html", details=Users.query.all(), message=message)
        except Exception as e:
            db.session.rollback()  
            print(e)
            message = "An error occurred while deleting the entry. Please check if reference to this entry exists in other tables."
            return render_template("home.html", details=Users.query.all(), message=message)
        

@app.route('/users/rename', methods=['GET', 'POST'])
def rename_table():
    global table_name
    if request.method == 'POST':
        new_table_name = request.form['new_table_name']
        try:
            db.session.execute(text(f"ALTER TABLE {table_name} RENAME TO {new_table_name}"))
            message = f"Table '{table_name}' renamed to '{new_table_name}' successfully"
            table_name = new_table_name
        except Exception as e:
            message = f"An error occurred while renaming the table: {str(e)}"
        return render_template("rename_user_table.html", message=message, table_name=table_name)
    return render_template("rename_user_table.html", table_name=table_name)

if __name__ == "__main__":
    table_name = "user_table"
    create_db()
    app.run(debug=True)