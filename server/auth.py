from flask_login import UserMixin
from database import db
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_oauthlib.client import OAuth
from database import db
import secrets

oauth = OAuth()

google = oauth.remote_app(
    'google',
    consumer_key='533702182800-0jte7ov5a124rri2skoj4fh3hml57bje.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

class Users(db.Model, UserMixin):
    __tablename__ = "user_table"
 
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=True)
    email_id = db.Column(db.String(255), nullable=False, unique=True)
    mobile_number = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='user')

    def get_id(self):
        return str(self.user_id)

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('home/login.html')

@auth.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('auth.google_authorized', _external=True))

@auth.route('/login/google/authorized')
@google.authorized_handler
def google_authorized(resp):
    access_token = resp['access_token']
    session['google_token'] = (access_token, '')
    user_info = google.get('userinfo')
    print(user_info.data)
    email = user_info.data['email']
    name = user_info.data.get('name')
    print(name)
    if email.endswith('@iitgn.ac.in'):
        user = Users.query.filter_by(email_id=email).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('home/signup.html', email_id=email)
    else:
        flash('Only users with @iitgn.ac.in email addresses are allowed.')
        return redirect(url_for('auth.login'))

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = Users.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) 

    login_user(user)
    return redirect(url_for('home'))

@auth.route('/signup', methods=['POST'])
def signup_post():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    mobile_number = request.form.get('mobile_number')
    email = request.form.get('email')
    try:
        new_user = Users(first_name=first_name, last_name=last_name, mobile_number=mobile_number, email_id=email)
        login_user(new_user)
        db.session.add(new_user)
        db.session.commit()
        db.session.close()
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        print(e)
        flash('An error occurred while adding the user. Please check your input.')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    session.pop('google_token', None)
    logout_user()
    return redirect(url_for('auth.login'))