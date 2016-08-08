try:
    from .models import User
except Exception:
    from models import User

import os
import sys
import csv
import datetime

user = User('test@mail.com')
user.register('test_user', 'test')

filename = sys.argv[1]
dir_path = os.path.abspath('test_data')
file_path = os.path.join(dir_path, "{}.csv".format(filename))


def job_period(period, day):
    day_to_num = dict(Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=5)
    init_day = datetime.date.today()
    day_delta = datetime.timedelta(days=day_to_num[day])
    today = init_day + day_delta
    period_list = period.split('-')
    start_time = datetime.datetime.combine(today, datetime.datetime.strptime(period_list[0], '%H:%M').time())
    end_time = datetime.datetime.combine(today, datetime.datetime.strptime(period_list[1], '%H:%M').time())
    return start_time, end_time

# print(job_period('12:55-14:33', 'tuesday'))


def project_period():
    init_day = datetime.datetime.today()
    last_day = init_day + datetime.timedelta(days=7)
    return init_day, last_day

# print(project_period())


with open(file_path) as f:
    cf = csv.DictReader(f, delimiter=',')
    project_period_obj = project_period()
    project_dict = dict(start_time=project_period_obj[0], end_time=project_period_obj[1])
    for row in cf:
        for key, value in row.items():
            if key != 'Period':
                project_dict['day'] = key
                project = user.add_project_by_name(value, **project_dict)
                job_period_obj = job_period(row['Period'], key)
                job_dict = dict(start_time=job_period_obj[0], end_time=job_period_obj[1])
                user.add_job_to_project(value + 'job', project, **job_dict)
# print(file_path)
