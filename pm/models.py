from pm import db
import time
from pm.const import TASK_STATUS
from sqlalchemy.dialects.mysql import BLOB, INTEGER, VARCHAR, TIMESTAMP


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(80), nullable=False, unique=True)
    staff_id = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.BigInteger, nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Integer, default=1)
    enable = db.Column(db.Integer,default=1)

    def __init__(self, user_name, staff_id, email, phone_number):
        self.user_name = user_name
        self.staff_id = staff_id
        self.email = email
        self.phone_number = phone_number
        self.password = phone_number

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def set_pwd(self, pwd):
        self.password = pwd

    def verify_pwd(self, pwd):
        if self.password == pwd:
            return True
        else:
            return False

    def __repr__(self):
        return "<User:{0}>".format(self.user_name)


class Need(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    need_name = db.Column(db.String(200), nullable=False)
    outer_sponsor = db.Column(db.String(50))
    inner_sponsor = db.Column(db.String(50))
    itsm_id = db.Column(db.String(50))
    need_desc = db.Column(db.String(500))
    project_id = db.Column(db.Integer)
    application_id = db.Column(db.Integer)
    create_person_id = db.Column(db.Integer, nullable=False)
    charge_person_id = db.Column(db.Integer)
    create_time = db.Column(db.String(20))
    plan_commit_time = db.Column(db.String(20))
    real_commit_time = db.Column(db.String(20))
    status = db.Column(db.Integer)
    parent_need_id = db.Column(db.Integer, default=-1)
    level_id = db.Column(db.Integer, default=1)
    work_load = db.Column(db.String(10))

    def __init__(self, need_name, outer_sponsor, inner_sponsor, itsm_id, need_desc, project_id, application_id,
                 create_person_id, charge_person_id, plan_commit_time, real_commit_time, status, parent_need_id,
                 level_id, work_load):
        self.need_name = need_name
        self.outer_sponsor = outer_sponsor
        self.inner_sponsor = inner_sponsor
        self.itsm_id = itsm_id
        self.need_desc = need_desc
        self.project_id = project_id
        self.application_id = application_id
        self.create_person_id = create_person_id
        self.charge_person_id = charge_person_id
        self.create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.plan_commit_time = plan_commit_time
        self.real_commit_time = real_commit_time
        self.status = status
        self.parent_need_id = parent_need_id
        self.level_id = level_id
        self.work_load = work_load

    def __repr__(self):
        return "<Need:{0}>".format(self.need_name)

    def to_json(self):
        return {
            'id': self.id,
            'need_name': self.need_name,
            'outer_sponsor': self.outer_sponsor,
            'inner_sponsor': self.inner_sponsor,
            'itsm_id': self.itsm_id,
            'need_desc': self.need_desc,
            'project_id': self.project_id,
            'application_id': self.application_id,
            'create_person_id': self.create_person_id,
            'charge_person_id': self.charge_person_id,
            'create_time': self.create_time,
            'plan_commit_time': self.plan_commit_time,
            'real_commit_time': self.real_commit_time,
            'status': self.status,
            'parent_need_id': self.parent_need_id,
            'level_id': self.level_id,
            'work_load': self.work_load
        }


# class NeedDetail(db.Model):
#    pass


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(200), nullable=False)
    project_manager_id = db.Column(db.Integer)
    build_year = db.Column(db.Integer)
    status = db.Column(db.Integer)

    def __init__(self, project_name, project_manager_id, build_year, status):
        self.project_name = project_name
        self.project_manager_id = project_manager_id
        self.build_year = build_year
        self.status = status

    def __repr__(self):
        return "<Project:{0}>".format(self.project_name)

    def to_json(self):
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_manager_id': self.project_manager_id,
            'build_year': self.build_year,
            'status': self.status
        }


class Application(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    application_name = db.Column(db.String(200), nullable=False)
    product_manager_id = db.Column(db.Integer)
    current_version = db.Column(db.String(10))
    status = db.Column(db.Integer)

    def __init__(self, application_name, product_manager_id, current_version, status):
        self.application_name = application_name
        self.product_manager_id = product_manager_id
        self.current_version = current_version
        self.status = status

    def __repr__(self):
        return "<Application:{0}>".format(self.application_name)

    def to_json(self):
        return {
            'id': self.id,
            'application_name': self.application_name,
            'product_manager_id': self.product_manager_id,
            'current_version': self.current_version,
            'status': self.status
        }


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stage_name = db.Column(db.String(200), default='')
    task_name = db.Column(db.String(200), default='')
    task_detail = db.Column(db.String(200), default='')
    need_id = db.Column(db.Integer)
    charge_person_id = db.Column(db.Integer)
    partner_person_id = db.Column(db.Integer)
    parent_task_id = db.Column(db.Integer)
    plan_start_time = db.Column(db.String(20))
    plan_finish_time = db.Column(db.String(20))
    real_start_time = db.Column(db.String(20))
    real_finish_time = db.Column(db.String(20))
    status = db.Column(db.Integer)
    processing_progress = db.Column(db.DECIMAL)
    comment = db.Column(db.String(250))
    create_time = db.Column(db.String(20))
    modify_time = db.Column(db.String(20))
    commit_time = db.Column(db.String(20))
    create_person_id = db.Column(db.Integer)
    modify_person_id = db.Column(db.Integer)
    level_id = db.Column(db.Integer)

    def __init__(self, stage_name, task_name, task_detail, need_id, charge_person_id, partner_person_id, parent_task_id,
                 plan_start_time, plan_finish_time, real_start_time, real_finish_time, status, processing_progress,
                 comment, modify_time, commit_time, create_person_id, modify_person_id, level_id):
        self.stage_name = stage_name
        self.task_name = task_name
        self.task_detail = task_detail
        self.need_id = need_id
        self.charge_person_id = charge_person_id
        self.partner_person_id = partner_person_id
        self.parent_task_id = parent_task_id
        self.plan_start_time = plan_start_time
        self.plan_finish_time = plan_finish_time
        self.real_start_time = real_start_time
        self.real_finish_time = real_finish_time
        self.status = status
        self.processing_progress = processing_progress
        self.comment = comment
        self.create_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.modify_time = modify_time
        self.commit_time = commit_time
        self.create_person_id = create_person_id
        self.modify_person_id = modify_person_id
        self.level_id = level_id

    def __repr__(self):
        return "<Task:{0}>".format(self.task_name)

    def to_json(self):
        return {
            'id': self.id,
            'stage_name': self.stage_name,
            'task_name': self.task_name,
            'task_detail': self.task_detail,
            'plan_start_time': self.plan_start_time,
            'plan_finish_time': self.plan_finish_time,
            'real_start_time': self.real_start_time,
            'real_finish_time': self.real_finish_time,
            'status': TASK_STATUS[self.status],
            'processing_progress': self.processing_progress,
            'comment': self.comment
        }


class Log(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    model = db.Column(db.String(50))
    action = db.Column(db.String(50))
    obj_id = db.Column(db.Integer)
    obj_name = db.Column(db.String(200))
    detail = db.Column(db.String(200))
    user_id = db.Column(db.Integer, nullable=False)
    log_time = db.Column(db.String(20), nullable=False)

    def __init__(self, model, action, obj_id, obj_name, detail, user_id, log_time):
        self.model = model
        self.action = action
        self.obj_id = obj_id
        self.obj_name = obj_name
        self.detail = detail
        self.user_id = user_id
        self.log_time = log_time

    def to_json(self):
        return {
            'id': self.id,
            'model': self.model,
            'action': self.action,
            'obj_id': self.obj_id,
            'obj_name': self.obj_name,
            'detail': self.detail,
            'user_id': self.user_id,
            'log_time': self.log_time
        }

    def __repr__(self):
        return "<Log:{0}>".format(self.id)


class Experience(db.Model):
    id = db.Column(INTEGER, autoincrement=True, primary_key=True)
    title = db.Column(VARCHAR(50), nullable=False)
    summary = db.Column(VARCHAR(200), nullable=False)
    url = db.Column(VARCHAR(100))
    type = db.Column(INTEGER, nullable=False)
    related_project_id = db.Column(INTEGER)
    related_application_id = db.Column(INTEGER)
    detail = db.Column(BLOB)
    create_person_id = db.Column(INTEGER, nullable=False)
    create_time = db.Column(TIMESTAMP, nullable=False)
    modify_person_id = db.Column(INTEGER)
    modify_time = db.Column(TIMESTAMP)
    modify_counts = db.Column(INTEGER, default=0, nullable=False)

    def __init__(self, title, summary, url, type, related_project_id, related_application_id, detail, create_person_id,
                 create_time):
        self.title = title
        self.summary = summary
        self.url = url
        self.type = type
        self.related_project_id = related_project_id
        self.related_application_id = related_application_id
        self.detail = detail
        self.create_person_id = create_person_id
        self.modify_person_id = create_person_id
        self.create_time = create_time
        self.modify_time = create_time

    def __repr__(self):
        return "<Experience:{0}>".format(self.title)
