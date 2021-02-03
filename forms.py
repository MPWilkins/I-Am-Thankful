from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.validators import ValidationError
from passlib.hash import sha256_crypt


# Inputs the user credintials into a database
class RegistrationForm(FlaskForm):
   name = StringField('Name', 
      [validators.Length(min=1, max=50)])
   username = StringField('Username', 
      [validators.Length(min=4, max=25)])
   password = PasswordField('Password', [
      validators.Length(min=8, max=99),
      validators.DataRequired(),
      validators.EqualTo('confirm', 
         message="Passwords do not match")
   ])
   confirm = PasswordField('Confirm Password')

   def validate_username(self, username):
      from app import User
      user_object = User.query.filter_by(username=username.data).first()
      if user_object:
         raise ValidationError("Username already taken.")


# Checks to make sure if username and password are valid
def login_error(form, field):
   from app import User
   username = form.username.data
   login_password = field.data
   user_object = User.query.filter_by(username=username).first()
   if user_object is None:
      raise ValidationError("Username or password is incorrect.")
   elif not sha256_crypt.verify(login_password, user_object.hashed_password):
      raise ValidationError("Username or password is incorrect.")  

# Log into User Session if entered successfully
class LoginForm(FlaskForm):
   username = StringField('Username', 
      [validators.InputRequired(message="Username required")])
   login_password = PasswordField('Password', 
      [validators.InputRequired(message="Password Required"), login_error])


# User is able to enter what they are thankful for that day.
class ThankfulEntryForm(FlaskForm):
   entry = StringField('What are you thankful for?',
      [validators.InputRequired(message="Please type what you are thankful for.")])