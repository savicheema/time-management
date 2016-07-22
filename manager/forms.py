from flask_wtf import Form
from wtforms import StringField, PasswordField, DateTimeField

class UserForm(Form):
    name = StringField('Username')
    password = PasswordField('Password')

class ProjectForm(Form):
    name = StringField('Project Name')
    start_time = DateTimeField('Start Time')
    end_time = DateTimeField('End Time')

    # members
    # clients