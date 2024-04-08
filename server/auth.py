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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    name = db.Column(db.String(1000))

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
        user = User.query.filter_by(email=email).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        else:
            # User doesn't exist, create a new user
            name = 'Someone'
            name = user_info.data.get('name')
            print(name)
            # Generate a unique token for password
            password_token = secrets.token_urlsafe(16)  # Generate a random URL-safe token
            new_user = User(email=email, name=name, password=password_token)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('home'))
    else:
        flash('Only users with @iitgn.ac.in email addresses are allowed.')
        return redirect(url_for('auth.login'))

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) 

    login_user(user, remember=remember)
    return redirect(url_for('home'))

@auth.route('/signup')
def signup():
    return render_template('home/signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    if email.endswith('@iitgn.ac.in'):
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.login'))
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login'))
    else:
        flash('Only users with @iitgn.ac.in email addresses are allowed.')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    session.pop('google_token', None)
    logout_user()
    return redirect(url_for('auth.login'))