import os # Imported the operating system to conceal secret key.

# Group of flask imports
from flask import Flask, render_template, redirect, url_for, session, request, logging, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from passlib.hash import sha256_crypt
from flask_moment import Moment

# importing from forms and importing dates
from forms import *
from datetime import datetime


app = Flask(__name__)


# Current state of server access, developement or production
ENV = 'prod'
if ENV == 'dev':
   app.debug = True
   app.secret_key = os.environ.get('Python_Secret_Key')
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('Python_Secret_Key')
elif ENV == 'prod':
   app.debug = False
   app.secret_key = os.environ.get('SP_Session')
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app)


# Configures and Initializes Flask-Migrate
moment = Moment(app)
moment.init_app(app)


# Configures and Initializes Flask-Login
login = LoginManager(app)
login.init_app(app)


# Database Table to store user credentials
class User(UserMixin, db.Model):
   __tablename__ = 'user'
   
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), nullable=False)
   username = db.Column(db.String(25), unique=True, nullable=False)
   hashed_password = db.Column(db.String(), nullable=False)
   entries = db.relationship('Entry', backref='user', lazy=True)

   def __init__(self, name, username, hashed_password):
        self.name = name
        self.username = username
        self.hashed_password = hashed_password


# Database table to store user entries
class Entry(db.Model):
   __tablename__ = 'entry'

   id = db.Column(db.Integer, primary_key=True)
   entry = db.Column(db.Text, nullable=False)
   entry_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

   def __init__(self, entry, entry_date, user_id):
        self.entry = entry
        self.entry_date = entry_date
        self.user_id = user_id


# Create database tables
db.create_all()


# Obtains the user's id for when they log in
@login.user_loader
def load_user(id):
   return User.query.get(int(id))


# Home Page
@app.route('/')
def home():
   return render_template('home.html')


# About Page
@app.route('/about')
def about():
   return render_template('about.html')


# User Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
   form = RegistrationForm(request.form)

   if form.validate_on_submit():
      password = form.password.data

      # Inserts the field entries into the User Table
      name = form.name.data
      username = form.username.data
      hashed_password = sha256_crypt.hash(password)

      registration_data = User(name,
                               username,
                               hashed_password)
      db.session.add(registration_data)
      db.session.commit()

      flash('Account Created. You may now log in.', 'success')
      return redirect(url_for('login'))

   return render_template('register.html', form=form)


# User Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()

   if form.validate_on_submit():
      user_object = User.query.filter_by(username=form.username.data).first()
      login_user(user_object)
      return redirect(url_for('IAmThankful'))

   return render_template('login.html', form=form)


# Entry Page/ Viewing Page
@app.route("/IAmThankful", methods=['GET', 'POST'])
@login_required 
def IAmThankful():
   form = ThankfulEntryForm()

   if form.validate_on_submit():
      # Obtains the active users id and inputs it along with the active UTC time and gratitude entry into the database.
      entry = form.entry.data
      entry_date = datetime.utcnow()
      user_id = current_user.id


      entry_data = Entry(entry,
                         entry_date,
                         user_id)
      db.session.add(entry_data)
      db.session.commit()

      return redirect(url_for('IAmThankful'))
   user_name = db.session.query(User.name).join(Entry). \
    filter(User.id == current_user.id).first()

   lists = Entry.query.filter(Entry.user_id == current_user.id)
   return render_template('IAmThankful.html', form=form, lists=lists, user_name=user_name)


# Delete user entries
@app.route("/delete/<int:id>", methods=['GET', 'POST']) 
def delete(id):
   delete_entry = Entry.query.get_or_404(id)

   
   db.session.delete(delete_entry)
   db.session.commit()
   flash('Entry Deleted', 'success')
   return redirect(url_for('IAmThankful'))


# Link that allows an individual to log out.
@app.route("/logout", methods=['GET'])
def logout():
   logout_user()
   flash('Log Out Successful. See you again soon.', 'success')
   return redirect(url_for('home'))


# Run App
if __name__ == '__main__':
   app.run()