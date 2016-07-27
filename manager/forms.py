from flask_wtf import Form
from wtforms import StringField, PasswordField, DateTimeField
from wtforms.fields.html5 import EmailField
from wtforms.validators import required
from datetime import datetime

class UserForm(Form):
    username = StringField('Username', [required()])
    email = EmailField('Email', [required()])
    password = PasswordField('Password', [required()])


class LoginForm(Form):
    email = EmailField('Email', [required()])
    password = PasswordField('Password', [required()])


class ProjectForm(Form):
    name = StringField('Project Name', [required()])
    start_time = DateTimeField('Start Time', default=datetime.now(), format="%b/%d/%y::%H:%M:%S")
    end_time = DateTimeField('End Time', default=datetime.now(), format="%b/%d/%y::%H:%M:%S")
    description = StringField('Description')
