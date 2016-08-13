from weakref import WeakKeyDictionary
from py2neo import Graph, Schema, Node, Relationship
from py2neo.database.status import ConstraintError
from datetime import datetime
import os
import uuid
import bcrypt
import sys

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', user='neo4j', password='neo')
schema = graph.schema


class WorkTimeDescriptor(object):
    formatter = "%b/%d/%y::%H:%M:%S"

    def __init__(self):
        self.now = datetime.now()
        self.data = WeakKeyDictionary()

    def __set__(self, instance, value):
        self.data[instance] = value

    def __get__(self, instance, owner):
        return self.data[instance].strftime(self.formatter)

    def __delete__(self, instance):
        pass


# USAGE
# s = Step(step_id)
# s.start(), s.stop(), s.complete(), s.suspend()
# s.start_time, s.create_time, s.end_time, s.name, s.description
class Step(object):
    start_time = WorkTimeDescriptor()
    create_time = WorkTimeDescriptor()
    end_time = WorkTimeDescriptor()

    time_keys = ['start_time', 'create_time', 'end_time']
    def __init__(self):
        self.name = name
        self.id = id
        self.status = None
        self.create_time = None
        self.members = []
        for key, value in kwargs.items():
            if key in self.time_keys and isinstance(value, str):
                val = datetime.strptime(value, WorkTimeDescriptor.formatter)
            else:
                val = kwargs.get(key, None)
            self.__setattr__(key, val)


# USAGE
# j = Job(job_id)
# j.start(), j.stop(), j.complete(), j.suspend()
# j.steps, j.start_time etc.
# p.add_step()
class Job(object):
    start_time = WorkTimeDescriptor()
    create_time = WorkTimeDescriptor()
    end_time = WorkTimeDescriptor()

    time_keys = ['start_time', 'create_time', 'end_time']
    def __init__(self, name, id, **kwargs):
        self.name = name
        self.id = id
        self.status = None
        self.create_time = None
        self.members = []
        for key, value in kwargs.items():
            if key in self.time_keys and isinstance(value, str):
                val = datetime.strptime(value, WorkTimeDescriptor.formatter)
            else:
                val = kwargs.get(key, None)
            self.__setattr__(key, val)

    def find(self, **kwargs):
        job_object = graph.find_one('Job', 'id', kwargs.get('id', self.id))
        return Job(job_object['name'], job_object['id'], **sanitize(job_object, 'name', 'id'))

    def save(self, project, user, **kwargs):
        # self.id = str(uuid.uuid4())
        self.create_time = datetime.now()
        self.members.append(user.username)

        # Add descriptor attributes like create_time, start_time etc of Project
        # to Project object dictionary so that they will be added to database
        for key in Project.__dict__.keys():
            if isinstance(Project.__dict__[key], WorkTimeDescriptor):
                try:
                    self.__dict__[key] = self.__getattribute__(key)
                except KeyError as e:
                    # import pdb
                    # pdb.set_trace()
                    print(e, key)

        project_object = graph.find_one('Project', 'id', project.id)
        job_object = Node('Job', **self.__dict__)
        rel = Relationship(project_object, 'HAS', job_object)
        graph.create(rel)
        return job_object, rel

    def delete(self):
        query = """
        MATCH(job:Job) WHERE job.id = {job_id}
        DETACH DELETE job;
        """
        return graph.run(query, job_id=self.id)


# USAGE
# p = Project(project_id)
# p.start(), p.stop(), p.complete(), p.suspend(), p.delete()
# p.jobs, p.job(1).steps, p.start_time etc.
# p.add_jobs(), p.add_step_to_job()
class Project(object):
    start_time = WorkTimeDescriptor()
    create_time = WorkTimeDescriptor()
    end_time = WorkTimeDescriptor()

    time_keys = ['start_time', 'create_time', 'end_time']
    # List of Variables used
    # name, status

    def __init__(self, name, id, **kwargs):
        self.name = name
        self.id = id
        self.status = None
        self.create_time = None
        self.members = []
        for key, value in kwargs.items():
            if key in self.time_keys and isinstance(value, str):
                val = datetime.strptime(value, WorkTimeDescriptor.formatter)
            else:
                val = kwargs.get(key, None)
            self.__setattr__(key, val)

    def find(self, **kwargs):
        project_object = graph.find_one('Project', 'id', kwargs.get('id', self.id))
        return Project(project_object['name'], project_object['id'], **sanitize(project_object, 'name', 'id'))

    def save(self, user_object):
        # self.id = str(uuid.uuid4())
        self.create_time = datetime.now()
        self.members.append(user_object['username'])

        # Add descriptor attributes like create_time, start_time etc of Project
        # to Project object dictionary so that they will be added to database
        for key in Project.__dict__.keys():
            if isinstance(Project.__dict__[key], WorkTimeDescriptor):
                try:
                    self.__dict__[key] = self.__getattribute__(key)
                except KeyError as e:
                    # import pdb
                    # pdb.set_trace()
                    print(e, key)

        project = Node('Project', **self.__dict__)
        rel = Relationship(user_object, 'WORKS_ON', project)
        graph.create(rel)
        return project, rel

    def delete(self):
        query = """
        MATCH(project:Project) WHERE project.id = {project_id}
        OPTIONAL MATCH (project)-[:HAS]-(job)
        DETACH DELETE project, job;
        """
        return graph.run(query, project_id=self.id)

    def start(self):
        self.status = 'active'
        # check start time issues and trigger start

    def stop(self):
        self.status = 'stopped'
        # check stop time issues and trigger stopping

    def complete(self):
        self.status = 'completed'
        # check end time issues and trigger ending

    def suspend(self):
        self.status = 'suspended'
        # check suspend time issues and trigger suspending


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


# USAGE
# user = User('name')
# user.register(), user.login(), user.logout(), user.reset_password()
# user.projects(), user.jobs(), user.project(1).jobs, user.job(1).steps
# user.add_project(), user.add_job_to_project(), user.add_step_to_job()
# user.delete_project(1), user.delete_job(1)
class User:
    # projects = []

    def __init__(self, email, **kwargs):
        self.username = None
        self.email = email
        for key, value in kwargs.items():
            if key is not 'email':
                self.__setattr__(key, kwargs.get(key, None))
        self.password = None

    def find(self):
        user = graph.find_one('User', 'email', self.email)
        return user

    def register(self, username, password, **kwargs):
        password_b = password.encode(encoding='utf-8')
        self.username = username
        self.password = bcrypt.hashpw(password_b, bcrypt.gensalt())
        self.name = self.username  # Hack for Neo4j Node label name
        if not self.find():
            user_node = Node('User', **self.__dict__)
            try:
                graph.merge(user_node, 'User', 'email')
            except ConstraintError as e:
                response = dict(success=False,
                                message="<p>Username <i>{}</i> already exists, choose another username</p>".
                                format(self.username))
            else:
                response = dict(success=True,
                                message="<p>User <i>{}</i> Registered successfully</p>".format(self.username))
            return response
        else:
            return dict(success=True, message="User already exists")

    def login(self, password):
        user_object = self.find()
        password_b = password.encode(encoding='utf-8')
        if not user_object:
            return dict(message="No user, {}, exists".format(self.email), success=False)
        elif bcrypt.checkpw(password_b, user_object['password'].encode(encoding='utf-8')):
            user = User(user_object['email'], **sanitize(user_object, 'email'))
            return dict(success=True, user=user)
        else:
            return dict(message="Incorrect Password", success=False)

    def add_project(self, name, **kwargs):
        project = Project(name, str(uuid.uuid4()), **kwargs)
        user_object = self.find()
        project_object, relationship_object = project.save(user_object=user_object)
        return Project(project_object['name'], project_object['id'], **sanitize(project_object, 'name', 'id'))

    def add_project_by_name(self, name, **kwargs):
        projects = self.projects()
        for data in projects:
            if name == data['project']['name']:
                print("Project already exists")
                return Project('dummy', data['project']['id'])

        return self.add_project(name, **kwargs)

    # Add filter params in kwargs to select user projects
    # user.projects(sort='date', create_time='time', start_time=.....)
    def projects(self, **kwargs):
        query = """
        MATCH (user:User)-[:WORKS_ON]-(project:Project)
        WHERE user.email = {email}
        RETURN project
        """
        result = graph.run(query, email=self.email)
        # import pdb
        # pdb.set_trace()
        return result

    def has_project(self, project_id):
        projects = self.projects(all=True)
        for project in projects:
            if project['project']['id'] == project_id:
                return True

        return False

    def delete_project(self, project_id):
        if self.has_project(project_id):
            try:
                Project('dummy', project_id).find().delete()
            except Exception:
                # Log exceptions in logfiles
                raise Exception
            else:
                return dict(success=True, message='Project, {}, is deleted successfully'.format(project_id))
        else:
            return dict(success=False, message='Project, {}, does not belong to you'.format(project_id))

    def add_job_to_project(self, name, project, **kwargs):
        job = Job(name, str(uuid.uuid4()), **kwargs)
        project = project.find()
        user_object = self.find()
        user = User(user_object['email'], **sanitize(user_object, 'email'))

        if not self.has_project(project.id):
            return dict(success=False, message="Nigga you ain't working on this project!")

        job_object, relationship_object = job.save(project=project, user=user)
        job = Job(job_object['name'], job_object['id'], **sanitize(job_object, 'name', 'id'))
        return dict(success=True, job=job)

    def jobs(self, *args, **kwargs):
        if kwargs.get('all'):
            query = """
            MATCH (user:User)-[:WORKS_ON]-(project:Project)-[:HAS]-(job:Job)
            WHERE user.email = {email}
            RETURN job, project
            """
        else:
            query = """
            MATCH (user:User)-[:WORKS_ON]-(project:Project)-[:HAS]-(job:Job)
            WHERE user.email = {email} and project.id IN {projects}
            RETURN job, project
            """
        result = graph.run(query, email=self.email, projects=args)
        return result

    def has_job(self, job_id):
        jobs = self.jobs(all=True)
        for job in jobs:
            if job['job']['id'] == job_id:
                return True

        return False

    def delete_job(self, job_id):
        if self.has_job(job_id):
            try:
                Job('dummy', job_id).find().delete()
            except Exception:
                # Log exceptions in logfiles
                raise Exception
            else:
                return dict(success=True, message='Job, {}, is deleted successfully'.format(job_id))
        else:
            return dict(success=False, message='Job, {}, does not belong to you'.format(job_id))

    def add_step_to_job(self, name, job_id):
        pass

    def complete_step(self, name, step_id):
        pass

    def complete_job(self, name, job_id):
        pass

    def complete_project(self, name, project_id):
        pass

if __name__=='__main__':
    user = User('savi@mail.com')
    user.register('username', 'password')
    login_object = user.login('password')
    # print(login_user.email, login_user.username)  #Password not returned

    project = user.add_project('first')
    # user.projects(all=True)

    job_object = user.add_job_to_project('first job', project)
    
    ## project deletion code
    if len(sys.argv) > 1 and sys.argv[1]=='project':
      delete_response = user.delete_project(project.id)
      print(delete_response['message'])
    else:
      print("Project deletion not required")

    ## job deletion code
    if len(sys.argv) > 1 and sys.argv[1]=='job' and job_object['success']:
      delete_response = user.delete_job(job_object['job'].id)
      print(delete_response['message'])
    else:
      print("Job deletion not required")
    # import pdb
    # pdb.set_trace()
