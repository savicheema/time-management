from flask_wtf import Form
from wtforms import StringField, PasswordField, DateTimeField
from wtforms.fields.html5 import EmailField
from wtforms.validators import required

class UserForm(Form):
    username = StringField('Username', [required()])
    email = EmailField('Email', [required()])
    password = PasswordField('Password', [required()])


class LoginForm(Form):
    email = EmailField('Email', [required()])
    password = PasswordField('Password', [required()])


class ProjectForm(Form):
    name = StringField('Project Name')
    start_time = DateTimeField('Start Time')
    end_time = DateTimeField('End Time')