from .models import User #, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap
from .forms import UserForm, ProjectForm, LoginForm

app = Flask(__name__)
Bootstrap(app)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    user_form = UserForm()
    if user_form.validate_on_submit():
        username = user_form.username.data
        email = user_form.email.data
        password = user_form.password.data
        # print(user_form.__dict__['_fields'])
        user_register = User(username).register(email, password)
        if user_register['success']:
            return user_register['message'], 200
        else:
            flash(user_register['message'])
    elif request.method == 'POST':
        # import pdb
        # pdb.set_trccace()
        flash('Wrong submission')
    return render_template('signup.html', user_form=user_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    return render_template('login.html', login_form=login_form)


@app.route('/user/<username>/project/', methods=['GET', 'POST'])
def add_project(username):
    # Login Required
    user = User(username).login('savi')


    # show form
    project_form = ProjectForm()
    # on submit
    # get user and create project

    # project_form = ProjectForm()
    # if form success:
    # project_data = dict(create_time=None, start_time=None, end_time=None)
    if user:
        project = user.add_project('first')
    # import pdb
    # pdb.set_trace()
    return render_template('project.html', project_form=project_form)
    # return '<p> Project added {0}, at time {1} with ID:{2}'.format(project.name, project.create_time, project.id), 200

