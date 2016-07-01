# -*- coding:utf-8 -*-
import sys

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField, DateField, \
    HiddenField
from wtforms.validators import DataRequired, StopValidation
from models import User, Project, Application, Need
import datetime

reload(sys)
sys.setdefaultencoding('utf8')


def check_project(form, field):
    project = Project.query.filter_by(project_name=field.data).first()
    if project is not None:
        raise StopValidation('该项目已存在!')


def check_application(form, field):
    application = Application.query.filter_by(application_name=field.data).first()
    if application is not None:
        raise StopValidation('该项目已存在!')


def check_need(form, field):
    need = Need.query.filter_by(need_name=field.data).first()

    if isinstance(form, ModifyNeedForm):
        if need is not None and need.id != int(form.need_id.data):
            raise StopValidation('该需求已存在!')
    else:
        if need is not None:
            raise StopValidation('该需求已存在!')


def check_sponsor(form, field):
    s1 = form.outer_sponsor.data.strip()
    s2 = form.inner_sponsor.data.strip()
    if s1 == '' and s2 == '':
        raise StopValidation('内部、外部发起人不能同时为空!')


def check_itsm(form, field):
    need = Need.query.filter_by(itsm_id=field.data.strip()).first()

    if isinstance(form, ModifyNeedForm):
        if need is not None and need.id != int(form.need_id.data):
            raise StopValidation('该需求已存在!')
    else:
        if need is not None:
            raise StopValidation('该需求已存在!')


class LoginForm(Form):
    staff_id = StringField('工号', validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    submit = SubmitField("登录")


class ProjectForm(Form):
    project_name = StringField("项目名称", [DataRequired(), check_project])
    project_manager = SelectField("项目负责人", coerce=int, choices=[])
    build_year = IntegerField("所属年份", default=2016)
    status = SelectField("状态", coerce=str, choices=[('2', '在建'), ('1', '意向'), ('3', '结项')])
    submit = SubmitField("增加")
    csrf_enabled = None

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        person_choices = [(u.id, u.user_name) for u in User.query.order_by('staff_id')]
        self.project_manager.choices = person_choices


class ApplicationForm(Form):
    person_choices = [(u.id, u.user_name) for u in User.query.order_by('staff_id')]
    application_name = StringField("系统名称", [DataRequired(), check_application])
    product_manger_id = SelectField("产品经理", coerce=int, choices=[])
    current_version = StringField("版本", [DataRequired()])
    status = SelectField("状态", coerce=str, choices=[('1', '活跃'), ('2', '沉默')])
    submit = SubmitField("增加")
    csrf_enabled = None

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        person_choices = [(u.id, u.user_name) for u in User.query.order_by('staff_id')]
        self.product_manger_id.choices = person_choices


class NeedForm(Form):
    need_name = StringField("需求名称", [DataRequired(), check_need])
    outer_sponsor = StringField("外部发起人", [check_sponsor])
    inner_sponsor = StringField("内部发起人", [check_sponsor])
    itsm_id = StringField("ITSM单号", [check_itsm])
    need_desc = TextAreaField("需求描述")
    work_load = StringField("工作量(人日)")
    project_id = SelectField("所属项目", coerce=int, choices=[])
    application_id = SelectField("所属系统", coerce=int, choices=[])
    charge_person_id = SelectField("需求负责人", coerce=int, choices=[])
    plan_commit_time = DateField("计划完成时间", [DataRequired()],
                                 default=datetime.datetime.strptime('2016-06-01', '%Y-%m-%d'))
    status = SelectField("状态", coerce=int, choices=[])
    parent_need_id = SelectField("父需求", coerce=int, choices=[], default=-1)
    submit = SubmitField("增加")
    csrf_enabled = None

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        project_choices = [(u.id, u.project_name) for u in Project.query.order_by('id')]
        project_choices.append((-1, '无'))
        self.project_id.choices = project_choices
        application_choices = [(u.id, u.application_name) for u in Application.query.order_by('id')]
        application_choices.append((-1, '无'))
        self.application_id.choices = application_choices
        person_choices = [(u.id, u.user_name) for u in User.query.order_by('staff_id')]
        self.charge_person_id.choices = person_choices
        status_choices = [(1, '待对接'), (2, '待分析'), (3, '待设计'), (4, '待实现'), (5, '待发布'), (6, '已完结')]
        self.status.choices = status_choices
        need_choices = [(u.id, u.need_name) for u in Need.query.filter_by(level_id=1).all()]
        need_choices.append((-1, '无'))
        self.parent_need_id.choices = need_choices


class ModifyNeedForm(Form):
    csrf_enabled = None
    need_name = StringField("需求名称", [DataRequired(), check_need])
    outer_sponsor = StringField("外部发起人", [check_sponsor])
    inner_sponsor = StringField("内部发起人", [check_sponsor])
    itsm_id = StringField("ITSM单号", [check_itsm])
    need_desc = TextAreaField("需求描述")
    work_load = StringField("工作量(人日)")
    project_id = SelectField("所属项目", coerce=int, choices=[])
    application_id = SelectField("所属系统", coerce=int, choices=[])
    charge_person_id = SelectField("需求负责人", coerce=int, choices=[])
    plan_commit_time = DateField("计划完成时间", [DataRequired()],
                                 default=datetime.datetime.strptime('2016-06-01', '%Y-%m-%d'))
    real_commit_time = StringField("实际完成时间", default=None)
    status = SelectField("状态", coerce=int, choices=[])
    parent_need_id = SelectField("父需求", coerce=int, choices=[], default=-1)
    create_person_id = HiddenField("需求创建人")
    need_id = HiddenField("需求ID")
    submit = SubmitField("修改")

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        project_choices = [(u.id, u.project_name) for u in Project.query.order_by('id')]
        project_choices.append((-1, '无'))
        self.project_id.choices = project_choices
        application_choices = [(u.id, u.application_name) for u in Application.query.order_by('id')]
        application_choices.append((-1, '无'))
        self.application_id.choices = application_choices
        person_choices = [(u.id, u.user_name) for u in User.query.order_by('staff_id')]
        self.charge_person_id.choices = person_choices
        status_choices = [(1, '待对接'), (2, '待分析'), (3, '待设计'), (4, '待实现'), (5, '待发布'), (6, '已完结')]
        self.status.choices = status_choices
        need_choices = [(u.id, u.need_name) for u in Need.query.filter_by(level_id=1).all()]
        need_choices.append((-1, '无'))
        self.parent_need_id.choices = need_choices
