from weakref import WeakKeyDictionary
from py2neo import Graph, Node, Relationship
from py2neo.database.status import ConstraintError
from datetime import datetime
import os
import uuid
import bcrypt

url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')

graph = Graph(url + '/db/data/', user='neo4j', password='neo')


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

    def __init__(self):
        pass


# USAGE
# j = Job(job_id)
# j.start(), j.stop(), j.complete(), j.suspend()
# j.steps, j.start_time etc.
# p.add_step()
class Job(object):
    start_time = WorkTimeDescriptor()
    create_time = WorkTimeDescriptor()
    end_time = WorkTimeDescriptor()

    def __init__(self):
        pass


# USAGE
# p = Project(project_id)
# p.start(), p.stop(), p.complete(), p.suspend()
# p.jobs, p.job(1).steps, p.start_time etc.
# p.add_jobs(), p.add_step_to_job()
class Project(object):
    start_time = WorkTimeDescriptor()
    create_time = WorkTimeDescriptor()
    end_time = WorkTimeDescriptor()

    # List of Variables used
    # name, status

    def __init__(self, name, **kwargs):
        self.name = name
        self.status = None
        self.create_time = datetime.now()
        self.id = None
        for key, value in kwargs.items():
            self.__setattr__(key, kwargs.get(key, None))

    def save(self, user):
        self.id = str(uuid.uuid4())
        # project_attribute_list = ['create_time', 'start_time', 'end_time']
        # [self.__dict__.update(key=) for key]
        for key in Project.__dict__.keys():
            if isinstance(Project.__dict__[key], WorkTimeDescriptor):
                try:
                    value = self.__getattribute__(key)
                    self.__dict__.update(key=value)
                except KeyError as e:
                    print(e, key)
        project = Node('Project', **self.__dict__)
        # import pdb
        # pdb.set_trace()
        rel = Relationship(user, 'WORKS_ON', project)
        graph.create(rel)
        return rel

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


# USAGE
# user = User('name')
# user.register(), user.login(), user.logout(), user.reset_password()
# user.projects, user.jobs, user.project(1).jobs, user.job(1).steps
# user.add_project(), user.add_job_to_project(), user.add_step_to_job()
class User:
    projects = []

    def __init__(self, username, **kwargs):
        self.username = username
        self.email = None
        self.password = None
        for key, value in kwargs.items():
            self.__setattr__(key, kwargs.get(key, None))

    def find(self):
        user = graph.find_one('User', 'email', self.email)
        return user

    def register(self, email, password, **kwargs):
        password_b = password.encode(encoding='utf-8')
        self.email = email
        self.password = bcrypt.hashpw(password_b, bcrypt.gensalt())
        self.name = self.username  # Hack for Neo4j Node label name
        if not self.find():
            user_node = Node('User', **self.__dict__)
            try:
                graph.merge(user_node, 'User', 'email')
                response = dict(success=True,
                                message="<p>User <i>{}</i> Registered successfully</p>".format(self.username))
            except ConstraintError as e:
                response = dict(success=False,
                                message="<p>Username <i>{}</i> already exists, choose another username</p>".
                                format(self.username))
            else:
                print("Registration Failed")
                return dict(success=False, message="Sorry!, Registration Failed")
            return response
        else:
            return dict(success=True, message="User already exists")

    def login(self, password):
        user = self.find()
        password_b = password.encode(encoding='utf-8')
        if user and bcrypt.checkpw(password_b, user['password'].encode(encoding='utf-8')):
            return self
        else:
            return None

    def add_project(self, name, **kwargs):
        project = Project(name, **kwargs)
        user = self.find()
        result = project.save(user)
        return project

    def add_job_to_project(self, name, project_id):
        pass

    def add_step_to_job(self, name, job_id):
        pass

    def complete_step(self, name, step_id):
        pass

    def complete_job(self, name, job_id):
        pass

    def complete_project(self, name, project_id):
        pass

if __name__=='__main__':
    project = Project('first')
    user = User('savi')
    import pdb
    pdb.set_trace()