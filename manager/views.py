from .models import User #, get_todays_recent_posts
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap
from .forms import UserForm

app = Flask(__name__)
Bootstrap(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    user_form = UserForm()
    if user_form.validate_on_submit():
        name = user_form.name.data
        password = user_form.password.data
        User(name).register(password)
        print(name, password)
        flash("Great Job, {}!".format(name), category='info')
    else:
        # import pdb
        # pdb.set_trccace()
        print("wrong")
        flash('Wrong submission', category='warning')
    return render_template('login.html', form=user_form)
    # return '<h1>Hello World!</h1>'


@app.route('/user/<username>/project/', methods=['GET', 'POST'])
def add_project(username):
    # Login Required
    user = User(username).login('savi')


    # show form
    # on submit
    # get user and create project

    # project_form = ProjectForm()
    # if form success:
    # project_data = dict(create_time=None, start_time=None, end_time=None)
    if user:
        project = user.add_project('first')
    # import pdb
    # pdb.set_trace()
    return '<p> Project added {0}, at time {1} with ID:{2}'.format(project.name, project.create_time, project.id), 200

