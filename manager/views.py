from .models import User, Project
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap
from .forms import UserForm, ProjectForm, LoginForm, JobForm
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)

# app.jinja_env.line_statement_prefix = '#'
# app.jinja_env.line_comment_prefix = '##'


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('summary', user_id='savitoj.cheema@gmail.com'), 301)


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    user_form = UserForm()
    if user_form.validate_on_submit():
        username = user_form.username.data
        email = user_form.email.data
        password = user_form.password.data
        # print(user_form.__dict__['_fields'])
        user_register = User(email).register(username, password)
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
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        login_object = User(email).login(password)
        if login_object['success']:
            return redirect(url_for('summary', user_id=login_object['user'].email), 301)
        else:
            flash(login_object['message'])
    return render_template('login.html', login_form=login_form)


@app.route('/user/<user_id>/project/', methods=['GET', 'POST'])
def project(user_id):
    # Login Required

    # Fetch all user's projects
    user = User(user_id)
    projects = user.projects(all=True)

    # make a form submission
    project_form = ProjectForm()
    if project_form.validate_on_submit():
        project_name = project_form.name.data
        project_result = user.add_project(project_name, **sanitize(project_form.__dict__, 'name', 'email'))
        if project_result:
            return "<p> You have added a new project, [{}]".format(project_result.name)

    return render_template('project.html', project_form=project_form, projects=projects, user_id=user_id)


# @app.route('/user/<user_id>/project/<project_id>/delete', methods=[''])


@app.route('/user/<user_id>/project/<project_id>/job/', methods=['GET', 'POST'])
def job(user_id, project_id):
    # Login Required

    user = User(user_id)
    project = Project('dummy', 'id').find(id=project_id)
    jobs = user.jobs(project_id, all=False)

    # import pdb
    # pdb.set_trace()
    # make a form submission
    job_form = JobForm()
    if job_form.validate_on_submit():
        job_name = job_form.name.data
        job_result = user.add_job_to_project(job_name, project, **sanitize(job_form.__dict__, 'name'))
        if not job_result['success']:
            flash(job_result['message'])
        else:
            flash("Your have added new job, [{}]".format(job_result['job'].name))
    return render_template('jobs.html', jobs=jobs, job_form=job_form, project=project, user_id=user_id)


@app.route('/user/<user_id>/summary', methods=['GET'])
def summary(user_id):
    user = User(user_id)
    flash("<p> User {} has successfully logged in!".format(user.email))
    summary = user.jobs(all=True).data()
    return render_template('summary.html', summary=summary,user_id=user_id)


def sanitize(dirty_object, *args):
    forbidden_keys = ['SECRET_KEY', 'meta', '_fields', 'csrf_token', '_errors', 'csrf_enabled', '_prefix']
    forbidden_keys += args
    # descriptor_keys = ['start_time', 'create_time', 'end_time']
    object_dict = dict(dirty_object)

    for key in forbidden_keys:
        if key in object_dict.keys():
            object_dict.pop(key)

    for key in object_dict.keys():
        if isinstance(object_dict[key], list):
            pass
        elif not isinstance(object_dict[key], str):
            object_dict[key] = object_dict[key].data

    return object_dict


