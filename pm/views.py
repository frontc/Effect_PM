# -*- coding:utf-8 -*-
import sys

from flask import render_template, g, redirect, url_for, session, flash, request, jsonify, send_file, \
    send_from_directory
from pm import app, lm, db
from models import User, Project, Application, Need, Task, Experience
from sql import SQL
from tool import nvl, join, genxls, clean, log
from forms import LoginForm, ProjectForm, ApplicationForm, NeedForm, ModifyNeedForm
from flask.ext.login import login_user, current_user, login_required, logout_user
import urllib2, json, time
from config import *

reload(sys)
sys.setdefaultencoding('utf8')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('index.html', task_status_choices=TASK_STATUS_LIST)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        input_staff_id = form.staff_id.data
        input_password = form.password.data
        user = User.query.filter(User.staff_id == input_staff_id, User.enable == 1).first()
        if user is None:
            flash("用户不存在!")
        elif user.verify_pwd(input_password):
            login_user(user)
            log('login', '登陆', g.user.id, user.user_name, '成功')
            flash("登录成功!")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))
        else:
            flash("密码错误!")
    return render_template('login.html', form=form)


@app.route("/settings")
@login_required
def settings():
    pass


@app.before_request
def before_request():
    g.user = current_user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/needs")
@login_required
def needs():
    return render_template('needs.html')


@app.route("/address")
@login_required
def address():
    return render_template('address.html')


@app.route('/_get_project_info')
@login_required
def _get_project_info():
    project_id = request.args.get('project_id', 0, type=int)
    project_info = Project.query.get(project_id).to_json()
    return jsonify(result=project_info)


@app.route("/setting_project", methods=['POST', 'GET'])
@login_required
def setting_project():
    # 表格信息区
    projects = db.engine.execute(SQL['PROJECT_INFO'])
    project_choices = [(p.id, p.project_name) for p in Project.query.order_by('id')]
    user_choices = [(p.id, p.user_name) for p in User.query.filter(User.enable == 1).order_by('id')]
    # 增加项目区
    add_form = ProjectForm()
    add_form.project_manager.choices = user_choices
    if add_form.validate_on_submit():
        if g.user.role == 0:
            try:
                new_project = Project(add_form.project_name.data, add_form.project_manager.data,
                                      add_form.build_year.data, add_form.status.data)
                db.session.add(new_project)
                db.session.commit()
                log('project', '增加项目', new_project.id, new_project.project_name, '成功')
                flash("项目添加成功!")
            except Exception, e:
                flash("无法添加项目!")
                print Exception, e
                return render_template('setting-project.html', data=projects, user_choices=user_choices,
                                       status_choices=PROJECT_STATUS, add_form=add_form,
                                       project_choices=project_choices, atr='show')
        else:
            flash("无权限操作!")
    else:
        if len(add_form.errors) > 0:
            return render_template('setting-project.html', data=projects, user_choices=user_choices,
                                   status_choices=PROJECT_STATUS, add_form=add_form, project_choices=project_choices,
                                   atr='show')
    return render_template('setting-project.html', data=projects, user_choices=user_choices,
                           status_choices=PROJECT_STATUS, add_form=add_form, project_choices=project_choices,
                           atr='hidden')


@app.route("/_modify_project", methods=["POST", "GET"])
@login_required
def _modify_project():
    if g.user.role == 0:
        try:
            db.session.query(Project).filter(Project.id == request.form['modify_project_id']). \
                update({'project_name': request.form['modify_project_name'], \
                        'project_manager_id': request.form['modify_project_manager_selector'], \
                        'build_year': request.form['modify_project_build_year'], \
                        'status': request.form['modify_project_status']}, synchronize_session='evaluate')
            db.session.commit()
            log('project', '修改项目', request.form['modify_project_id'], request.form['modify_project_name'], '成功')
            flash("项目修改成功!")
        except Exception, e:
            flash("项目修改失败!")
            print Exception, e
    else:
        flash("无权限操作!")
    return redirect(url_for("setting_project"))


@app.route('/_get_application_info')
@login_required
def _get_application_info():
    application_id = request.args.get('application_id', 0, type=int)
    application_info = Application.query.get(application_id).to_json()
    return jsonify(result=application_info)


@app.route("/setting_application", methods=['POST', 'GET'])
@login_required
def setting_application():
    # 表格信息区
    applications = db.engine.execute(SQL['APPLICATION_INFO'])
    application_choices = [(p.id, p.application_name) for p in Application.query.order_by('id')]
    user_choices = [(p.id, p.user_name) for p in User.query.filter(User.enable == 1).order_by('id')]
    status_choices = APPLICATION_STATUS
    # 增加项目区
    add_form = ApplicationForm()
    add_form.product_manger_id.choices = user_choices
    if add_form.validate_on_submit():
        if g.user.role == 0:
            try:
                new_application = Application(add_form.application_name.data, add_form.product_manger_id.data,
                                              add_form.current_version.data, add_form.status.data)
                db.session.add(new_application)
                db.session.commit()
                log('application', '增加系统', new_application.id, new_application.application_name, '成功')
                flash("系统添加成功!")
            except Exception, e:
                flash("无法添加系统!")
                print Exception, e
                return render_template('setting-application.html', data=applications, user_choices=user_choices,
                                       status_choices=status_choices, add_form=add_form,
                                       application_choices=application_choices, atr='show')
        else:
            flash("无权限操作!")
    else:
        if len(add_form.errors) > 0:
            return render_template('setting-application.html', data=applications, user_choices=user_choices,
                                   status_choices=status_choices, add_form=add_form,
                                   application_choices=application_choices, atr='show')
    return render_template('setting-application.html', data=applications, user_choices=user_choices,
                           status_choices=status_choices, add_form=add_form, application_choices=application_choices,
                           atr='hidden')


@app.route("/_modify_application", methods=["POST", "GET"])
@login_required
def _modify_application():
    if not g.user.role:
        try:
            db.session.query(Application).filter(Application.id == request.form['modify_application_id']). \
                update({'application_name': request.form['modify_application_name'], \
                        'product_manager_id': request.form['modify_product_manager_selector'], \
                        'current_version': request.form['modify_version'], \
                        'status': request.form['modify_status']}, synchronize_session='evaluate')
            db.session.commit()
            log('application', '修改系统', request.form['modify_application_id'], request.form['modify_application_name'],
                '成功')
            flash("系统修改成功!")
        except Exception, e:
            flash("系统修改失败!")
            print Exception, e
    else:
        flash("无权限操作!")
    return redirect(url_for("setting_application"))


@app.route("/add_need", methods=["POST", "GET"])
@login_required
def add_need():
    form = NeedForm()
    project_choices = [(u.id, u.project_name) for u in Project.query.order_by('id')]
    project_choices.append((-1, '无'))
    application_choices = [(u.id, u.application_name) for u in Application.query.order_by('id')]
    application_choices.append((-1, '无'))
    person_choices = [(u.id, u.user_name) for u in User.query.filter(User.enable == 1).order_by('staff_id')]
    need_choices = [(u.id, u.need_name) for u in Need.query.filter(Need.level_id == 1).all()]
    need_choices.insert(0, (-1, '无'))
    form.charge_person_id.choices = person_choices
    form.project_id.choices = project_choices
    form.application_id.choices = application_choices
    form.parent_need_id.choices = need_choices
    if form.validate_on_submit():
        print form.outer_sponsor.data
        print form.inner_sponsor.data
        auto_level_id = 2
        if form.parent_need_id.data == -1:
            auto_level_id = 1
        try:
            new_need = Need(form.need_name.data.strip(),
                            form.outer_sponsor.data.strip(),
                            form.inner_sponsor.data.strip(),
                            form.itsm_id.data.strip(),
                            form.need_desc.data,
                            form.project_id.data,
                            form.application_id.data,
                            g.user.id,
                            form.charge_person_id.data,
                            form.plan_commit_time.data,
                            None,
                            form.status.data,
                            form.parent_need_id.data,
                            auto_level_id,
                            form.work_load.data.strip())
            db.session.add(new_need)
            db.session.commit()
            log('need', '增加需求', new_need.id, new_need.need_name, '成功')
            flash("需求添加成功!")
            return redirect(url_for('needs'))
        except Exception, e:
            print Exception, e
            flash("需求添加失败!")
    return render_template("add-need.html", form=form)


@app.route("/modify_need/<int:need_id>",methods=['POST','GET'])
@login_required
def modify_need(need_id):
    form = ModifyNeedForm()
    project_choices = [(u.id, u.project_name) for u in Project.query.order_by('id')]
    project_choices.insert(0, (-1, '无'))
    application_choices = [(u.id, u.application_name) for u in Application.query.order_by('id')]
    application_choices.insert(0, (-1, '无'))
    person_choices = [(u.id, u.user_name) for u in User.query.filter(User.enable == 1).order_by('staff_id')]
    need_choices = [(u.id, u.need_name) for u in Need.query.filter(Need.level_id == 1).all()]
    need_choices.insert(0, (-1, '无'))
    form.project_id.choices = project_choices
    form.charge_person_id.choices = person_choices
    form.application_id.choices = application_choices
    form.parent_need_id.choices = need_choices

    if form.validate_on_submit():
        if g.user.role == 0 or g.user.id == form.create_person_id.data or g.user.id == form.charge_person_id.data:
            try:
                auto_level_id = 2
                if form.parent_need_id.data == -1:
                    auto_level_id = 1
                db.session.query(Need).filter(Need.id == request.form['need_id']). \
                    update({'need_name': request.form['need_name'], \
                            'outer_sponsor': request.form['outer_sponsor'], \
                            'inner_sponsor': request.form['inner_sponsor'], \
                            'itsm_id': request.form['itsm_id'], \
                            'need_desc': request.form['need_desc'], \
                            'work_load': request.form['work_load'], \
                            'project_id': request.form['project_id'], \
                            'application_id': request.form['application_id'], \
                            'charge_person_id': request.form['charge_person_id'], \
                            'plan_commit_time': request.form['plan_commit_time'], \
                            'real_commit_time': request.form['real_commit_time'], \
                            'status': request.form['status'], \
                            'parent_need_id': request.form['parent_need_id'], \
                            'level_id': auto_level_id
                            }, synchronize_session='evaluate')
                db.session.commit()
                log('need', '修改需求', request.form['need_id'], request.form['need_name'], '成功')
                flash("需求修改成功!")
                return redirect(url_for('needs'))
            except Exception, e:
                flash("需求修改失败!")
                print Exception, e
        else:
            flash("权限不足!只有需求创建人拥有修改权限!")
    else:
        need = db.session.query(Need).filter(Need.id == need_id).first()
        form.need_name.data = need.need_name
        form.status.data = need.status
        form.outer_sponsor.data = need.outer_sponsor
        form.inner_sponsor.data = need.inner_sponsor
        form.itsm_id.data = need.itsm_id
        form.need_desc.data = need.need_desc
        form.work_load.data = need.work_load
        form.project_id.data = need.project_id
        form.application_id.data = need.application_id
        form.charge_person_id.data = need.charge_person_id
        form.plan_commit_time.data = str(need.plan_commit_time)
        form.real_commit_time.data = nvl(need.real_commit_time)
        form.parent_need_id.data = need.parent_need_id
        form.create_person_id.data = need.create_person_id
        form.need_id.data = need_id
    return render_template("modify-need.html", form=form)


@app.route('/_get_need_info')
@login_required
def _get_need_info():
    need_name = request.args.get('need_name', "hello", type=str)
    need_info = Need.query.filter_by(need_name=need_name).first().to_json()
    return jsonify(result=need_info)


@app.route('/plan')
@login_required
def plan():
    sql = SQL['TASK_LIST'].format('')
    task_list = db.engine.execute(sql)
    task_list_data = []
    for n in task_list:
        row = {'id': n[0],
               'stage_name': n[1],
               'task_name': n[2],
               'task_detail': n[3],
               'charge_person_name': n[4],
               'partner_person_name': n[5],
               'plan_start_time': n[6],
               'plan_finish_time': n[7],
               'real_start_time': n[8],
               'real_finish_time': n[9],
               'processing_progress': n[10],
               'status': n[11],
               'comment': n[12],
               'need_name': n[13]
               }
        task_list_data.append(row)
    users = User.query.all()
    user_list_data = []
    for user in users:
        user_list_data.append(user.user_name)
    needs = Need.query.all()
    need_list_data = []
    for need in needs:
        need_list_data.append(need.need_name)
    status_list_data = ['未开始', '执行中', '已暂停', '已作废', '已完成']
    project_choices = [(p.id, p.project_name) for p in Project.query.order_by('id')]
    application_choices = [(p.id, p.application_name) for p in Application.query.order_by('id')]
    user_choices = [(p.id, p.user_name) for p in User.query.order_by('id')]
    return render_template("plan.html", initdata=task_list_data, user_list=user_list_data, need_list=need_list_data,
                           status_list=status_list_data, project_choices=project_choices,
                           application_choices=application_choices, user_choices=user_choices)


@app.route('/_upload_task', methods=['POST', 'GET'])
@login_required
def _upload_task():
    req_data = json.loads(request.get_data())
    task_data = req_data['data']
    del_row = req_data['del']
    del_row = list(set(del_row))  # 去重
    status_list_dict = {'未开始': '1', '执行中': '2', '已暂停': '3', '已作废': '4', '已完成': '5'}
    try:
        for row in task_data:
            if row[1] is None and row[2] is None and row[3] is None:  # 过滤空行
                continue
            row[4] = db.session.query(User.id).filter(User.user_name == row[4]).first()[0]  # 转换人员名称到编码
            row[10] = status_list_dict.get(str(row[10]))  # 转换状态到编码
            row[12] = db.session.query(Need.id).filter(Need.need_name == row[12]).first()[0]  # 转换需求名称到编码
            if row[0] is None:  # 新增
                row = nvl(row)
                insert_sql = SQL['NEW_TASK'].format(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                                    row[9],
                                                    row[10], row[11], row[12], g.user.id,
                                                    time.strftime('%Y-%m-%d', time.localtime(time.time())))
                db.engine.execute(insert_sql)
                print "new:" + insert_sql
                log('task', '增加任务', None, row[1] + '-' + row[2] + '-' + row[3], '成功')
                continue
            # 修改
            row = nvl(row)
            for i in del_row:  # 去除撤销的删除
                if i == row[0]:
                    del_row.remove(i)
            if row[9] == 1 or row[10] == '5':
                commit_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            else:
                commit_time = ''
            update_sql = SQL['UPDATE_TASK'].format(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                                                   row[9],
                                                   row[10], row[11], row[12], g.user.id,
                                                   time.strftime('%Y-%m-%d', time.localtime(time.time())), commit_time,
                                                   row[0])
            print "update:" + update_sql
            db.engine.execute(update_sql)
            # log('task', '修改任务', row[0], row[1] + '-' + row[2] + '-' + row[3], '成功')

        # 删除
        if len(del_row) > 0:
            delete_sql = SQL['DELETE_TASK'].format(join(del_row))
            print "delete:" + delete_sql
            db.engine.execute(delete_sql)
            for i in del_row:
                if i is not None and i > 0:
                    log('task', '删除任务', i, '', '成功')
    except Exception, e:
        print Exception, e
        return '服务异常!'
    return '提交成功!'


@app.route('/_refresh_task', methods=['POST', 'GET'])
@login_required
def _refresh_task():
    req_data = json.loads(request.get_data())
    date_id = req_data['select_date']
    project_id = req_data['select_project']
    application_id = req_data['select_application']
    user_id = req_data['select_user']
    where = []
    where.append("charge_person_id ={0}".format(user_id)) if int(user_id) > 0 else True
    where.append("plan_start_time >='{0}'".format(date_id)) if len(date_id) > 5 else True
    where.append(
        "need_id IN (select id from need where need.project_id={0})".format(project_id)) if int(
        project_id) > 0 else True
    where.append(
        "need_id IN (select id from need where need.application_id={0})".format(
            application_id)) if int(application_id) > 0 else True

    sql = SQL['TASK_LIST'].format('where ' + ' and '.join(where)) if where else SQL['TASK_LIST'].format('')
    task_list = db.engine.execute(sql)
    task_list_data = []
    for n in task_list:
        row = {'id': n[0],
               'stage_name': n[1],
               'task_name': n[2],
               'task_detail': n[3],
               'charge_person_name': n[4],
               'partner_person_name': n[5],
               'plan_start_time': n[6],
               'plan_finish_time': n[7],
               'real_start_time': n[8],
               'real_finish_time': n[9],
               'processing_progress': n[10],
               'status': n[11],
               'comment': n[12],
               'need_name': n[13]
               }
        task_list_data.append(row)
    return jsonify(result=task_list_data, msg='刷新成功!')


@app.route('/_download_task', methods=['POST', 'GET'])
@login_required
def _download_task():
    req_data = json.loads(request.get_data())
    task_data = req_data['data']
    header_data = [u'ID', u'阶段', u'工作项', u'任务明细', u'负责人', u'预计开始时间', u'预计结束时间', u'实际开始时间', u'实际结束时间', u'进度', u'状态',
                   u'备注', u'需求名称']
    file_name = genxls(header_data, task_data)
    return file_name


@app.route('/download/<int:file_name>')
@login_required
def download(file_name):
    file_name = str(file_name) + '.xls'
    return send_from_directory(app.config['DOWNLOAD_DIRECTORY'], file_name, as_attachment=True)


@app.route('/_clean', methods=['POST'])
@login_required
def _clean():
    req_data = json.loads(request.get_data())
    result = clean(req_data['data'])
    return result


@app.route('/_get_overview_info')
@login_required
def _get_overview_info():
    if g.user.role == 0:
        all_projects = Project.query.filter(1 == 1).count()
        on_projects = Project.query.filter(Project.status == 3).count()
        all_applications = Application.query.filter(1 == 1).count()
        on_applications = Application.query.filter(Application.status == 1).count()
        all_needs = Need.query.filter(1 == 1).count()
        on_needs = Need.query.filter(Need.status != 6).count()
        all_tasks = Task.query.filter(1 == 1).count()
        on_tasks = Task.query.filter(Task.status.in_([1, 2, 3])).count()
    else:
        all_projects = Project.query.filter(Project.project_manager_id == g.user.id).count()
        on_projects = Project.query.filter(Project.project_manager_id == g.user.id, Project.status == 3).count()
        all_applications = Application.query.filter(Application.product_manager_id == g.user.id).count()
        on_applications = Application.query.filter(
            Application.product_manager_id == g.user.id, Application.status == 1).count()
        all_needs = Need.query.filter(Need.charge_person_id == g.user.id).count()
        on_needs = Need.query.filter(Need.charge_person_id == g.user.id, Need.status != 6).count()
        all_tasks = Task.query.filter(Task.charge_person_id == g.user.id).count()
        on_tasks = Task.query.filter(Task.charge_person_id == g.user.id, Task.status.in_([1, 2, 3])).count()
    return jsonify(all_projects=all_projects, on_projects=on_projects, all_applications=all_applications,
                   on_applications=on_applications, all_needs=all_needs, on_needs=on_needs,
                   all_tasks=all_tasks, on_tasks=on_tasks)


@app.route('/_get_task_info')
@login_required
def _get_task_info():
    todo_task_nums = Task.query.filter(Task.charge_person_id == g.user.id,
                                       Task.status.in_([1, 2, 3]),
                                       Task.plan_start_time <= time.strftime('%Y-%m-%d',
                                                                             time.localtime(time.time()))).count()
    done_task_nums = Task.query.filter(Task.charge_person_id == g.user.id,
                                       Task.real_finish_time == time.strftime('%Y-%m-%d',
                                                                              time.localtime(time.time())),
                                       Task.status == 5).count()
    todo_task_list = Task.query.filter(Task.charge_person_id == g.user.id,
                                       Task.status.in_([1, 2, 3]),
                                       Task.plan_start_time <= time.strftime('%Y-%m-%d',
                                                                             time.localtime(time.time()))).all()
    done_task_list = Task.query.filter(Task.charge_person_id == g.user.id,
                                       Task.real_finish_time == time.strftime('%Y-%m-%d',
                                                                              time.localtime(time.time())),
                                       Task.status == 5).all()
    for i in range(len(todo_task_list)):
        todo_task_list[i] = todo_task_list[i].to_json()
    for i in range(len(done_task_list)):
        done_task_list[i] = done_task_list[i].to_json()
    return jsonify(todo_task_nums=todo_task_nums,
                   done_task_nums=done_task_nums,
                   todo_task_list=todo_task_list,
                   done_task_list=done_task_list)


@app.route('/_update_task', methods=['POST'])
@login_required
def _update_task():
    req_data = json.loads(request.get_data())
    commit_time = None
    if req_data['status'] == '已完成':
        commit_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    modify_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    status_index = 1
    for i in range(len(TASK_STATUS_LIST)):
        if TASK_STATUS_LIST[i][1] == req_data['status']:
            status_index = TASK_STATUS_LIST[i][0]
            break
    try:
        db.session.query(Task).filter(Task.id == req_data['id']).update(
            {
                'real_start_time': req_data['startdate'],
                'real_finish_time': req_data['finishdate'],
                'processing_progress': int(req_data['progress']) / 100.0,
                'status': status_index,
                'comment': req_data['comment'],
                'modify_time': modify_time,
                'commit_time': commit_time,
                'modify_person_id': g.user.id
            }, synchronize_session='evaluate')
        db.session.commit()
        taskObj = Task.query.filter(Task.id == req_data['id']).first()
        log('task', '更新任务', req_data['id'], taskObj.stage_name + '-' + taskObj.task_name + '-' + taskObj.task_detail,
            '成功')
        return 'ok'
    except Exception, e:
        print Exception, e
        return 'false'


@app.route('/_get_activity', methods=['POST'])
@login_required
def _get_activity():
    req_data = json.loads(request.get_data())
    limits = int(req_data['limits'])
    sql = SQL['ACTIVITY_LIST'].format(g.user.id)
    activities = db.engine.execute(sql)
    activity_list = []
    counter = 0
    for item in activities:
        activity_list.append(item[0])
        counter += 1
        if counter == limits or counter == 50:
            break
    return jsonify(result=activity_list)


@app.route('/_quick_add_share', methods=['POST'])
@login_required
def _quick_add_share():
    req_data = json.loads(request.get_data())
    try:
        new_experience = Experience(req_data['title'], req_data['summary'], req_data['url'], 1, None, None, None,
                                    g.user.id,
                                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        db.session.add(new_experience)
        db.session.commit()
        log('experience', '增加知识', new_experience.id, new_experience.title, '成功')
        return 'ok'
    except Exception, e:
        print Exception, e
        return 'false'


@app.route('/experience')
@login_required
def experience():
    return render_template('experience.html')


@app.route('/worklog')
@login_required
def worklog():
    return render_template('worklog.html')


@app.route('/_get_experience_list')
@login_required
def _get_experience_list():
    order = request.args.get('order')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    keyword = request.args.get('keyword')
    total_sql = SQL['EXPERIENCE_TOTAL'].format(keyword)
    total = db.engine.execute(total_sql).first()['total']
    list_sql = SQL["EXPERIENCE_LIST"].format(keyword, int(offset) * int(limit), limit)
    list = db.engine.execute(list_sql)
    o = []
    for i in list:
        row = {
            "id": i[0],
            "title": i[1],
            "summary": i[2],
            "type": EXPERIENCE_TYPE_DICT[i[3]],
            "related_project_name": i[4],
            "related_application_name": i[5],
            "modify_person_name": i[6],
            "modify_time": str(i[7])[0:10]
        }
        o.append(row)
    return jsonify(total=total, rows=o)


@app.route('/_del_experience', methods=['POST'])
@login_required
def _del_experience():
    req_data = json.loads(request.get_data())
    id = req_data['id']
    try:
        title = db.session.query(Experience).filter(Experience.id == id[0]).first().title
        db.session.query(Experience).filter(Experience.id == id[0]).delete(synchronize_session='evaluate')
        db.session.commit()
        log('experience', '删除知识', id, title, '成功')
        return 'ok'
    except Exception, e:
        print Exception, e
        return 'false'


@app.route('/add_experience')
@login_required
def add_experience():
    project_choices = [(p.id, p.project_name) for p in Project.query.order_by('id')]
    application_choices = [(p.id, p.application_name) for p in Application.query.order_by('id')]
    return render_template("add-experience.html", experience_type_list=EXPERIENCE_TYPE_LIST,
                           project_choices=project_choices, application_choices=application_choices)


@app.route('/_add_experience', methods=['POST'])
@login_required
def _add_experience():
    req_data = json.loads(request.get_data())
    title = req_data['title'].encode('utf8')
    summary = req_data['summary'].encode('utf8')
    experience_type = req_data['type'].encode('utf8')
    url = req_data['url'].encode('utf8')
    project = req_data['project'].encode('utf8')
    application = req_data['application'].encode('utf8')
    print type(req_data['markupStr'])
    print req_data['markupStr']
    detail = req_data['markupStr'].encode('utf8')
    print detail
    if len(detail) < 13:
        detail = None
    try:
        new_experience = Experience(title, summary, url, experience_type, project, application, detail, g.user.id,
                                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        db.session.add(new_experience)
        db.session.commit()
        log('experience', '增加知识', new_experience.id, new_experience.title, '成功')
    except Exception, e:
        print Exception, e
        flash('出现未知错误!')
        return 'false'
    flash('新增成功!')
    return 'ok'


@app.route('/experience_detail/<int:exp_id>')
@login_required
def experience_detail(exp_id):
    exp = Experience.query.filter(Experience.id == exp_id).first()
    for item in EXPERIENCE_TYPE_LIST:
        if exp.type == item[0]:
            exp.type = item[1]
            break
    if exp.related_project_id > 0:
        exp.related_project_id = Project.query.get(exp.related_project_id).project_name
    else:
        exp.related_project_id = ''
    if exp.related_application_id > 0:
        exp.related_application_id = Application.query.get(exp.related_application_id).application_name
    else:
        exp.related_application_id = ''
    exp.create_person_id = User.query.get(exp.create_person_id).user_name
    exp.modify_person_id = User.query.get(exp.modify_person_id).user_name
    if exp.detail is None:
        exp.detail = '无详细描述!'
    return render_template('experience-detail.html', exp=exp)


@app.route('/modify_experience/<int:exp_id>')
@login_required
def modify_experience(exp_id):
    exp = Experience.query.filter(Experience.id == exp_id).first()
    project_choices = [(p.id, p.project_name) for p in Project.query.order_by('id')]
    application_choices = [(p.id, p.application_name) for p in Application.query.order_by('id')]
    return render_template("modify-experience.html", experience_type_list=EXPERIENCE_TYPE_LIST,
                           project_choices=project_choices, application_choices=application_choices, exp=exp)


@app.route('/_modify_experience', methods=['POST'])
@login_required
def _modify_experience():
    req_data = json.loads(request.get_data())
    id = req_data['id']
    title = req_data['title'].encode('utf8')
    summary = req_data['summary'].encode('utf8')
    experience_type = req_data['type'].encode('utf8')
    url = req_data['url'].encode('utf8')
    project = req_data['project'].encode('utf8')
    application = req_data['application'].encode('utf8')
    print type(req_data['markupStr'])
    print req_data['markupStr']
    detail = req_data['markupStr'].encode('utf8')
    print detail
    if len(detail) < 13:
        detail = None
    try:
        modify_counts = Experience.query.get(int(id)).modify_counts
        db.session.query(Experience).filter(Experience.id == int(id)).update({'title': title,
                                                                              'summary': summary,
                                                                              'type': experience_type,
                                                                              'url': url,
                                                                              'related_project_id': project,
                                                                              'related_application_id': application,
                                                                              'detail': detail,
                                                                              'modify_person_id': g.user.id,
                                                                              'modify_time': time.strftime(
                                                                                  '%Y-%m-%d %H:%M:%S',
                                                                                  time.localtime(time.time())),
                                                                              'modify_counts': modify_counts + 1
                                                                              }, synchronize_session='evaluate')
        db.session.commit()
        log('experience', '修改知识', id, title, '成功')
    except Exception, e:
        print Exception, e
        flash('出现未知错误!')
        return 'false'
    flash('修改成功!')
    return 'ok'


@app.route('/_get_experience', methods=['POST'])
@login_required
def _get_experience():
    req_data = json.loads(request.get_data())
    limits = int(req_data['limits'])
    sql = SQL['EXP_LIST']
    exps = db.engine.execute(sql)
    exp_list = []
    counter = 0
    for n in exps:
        if len(n[2]) < 5:
            url = '/experience_detail/' + str(n[0])
        else:
            url = n[2]
        row = {'id': n[0],
               'title': n[1],
               'url': url,
               'summary': n[3],
               'user': n[4],
               'modify_time': n[5],
               'type': n[6]
               }
        exp_list.append(row)
        counter += 1
        if counter == limits or counter == 50:
            break
    return jsonify(result=exp_list)


@app.route('/_get_user_list')
@login_required
def _get_user_list():
    order = request.args.get('order')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    keyword = request.args.get('keyword')
    total_sql = SQL['USER_TOTAL'].format(keyword)
    total_result = db.engine.execute(total_sql).first()['total']
    list_sql = SQL["USER_LIST"].format(keyword, int(offset) * int(limit), limit, order)
    list_result = db.engine.execute(list_sql)
    o = []
    for i in list_result:
        row = {
            "id": i[0],
            "user_name": i[1],
            "staff_id": i[2],
            "email": i[3],
            "phone_number": i[4]
        }
        o.append(row)
    return jsonify(total=total_result, rows=o)


@app.route('/_del_user', methods=['POST'])
@login_required
def _del_user():
    req_data = json.loads(request.get_data())
    user_id = int(req_data['id'][0])
    if not g.user.role:
        try:
            if Project.query.filter(Project.project_manager_id == user_id, Project.status != 3).count():
                return '该用户所负责的项目未结项!'
            if Application.query.filter(Application.product_manager_id == user_id).count():
                return '该用户是系统的负责人!'
            if Need.query.filter(Need.charge_person_id == user_id, Need.status != 6).count():
                return '该用户有未完成的需求!'
            if Task.query.filter(Task.charge_person_id == user_id, Task.status != 4, Task.status != 5).count():
                return '该用户有未完成的任务!'
            user_name = db.session.query(User).filter(User.id == user_id).first().user_name
            db.session.query(User).filter(User.id == user_id).update({'enable': 0}, synchronize_session='evaluate')
            db.session.commit()
            log('system', '删除用户', user_id, user_name, '成功')
            return 'ok'
        except Exception, e:
            print Exception, e
            return '删除用户失败!'
    else:
        return '您无权删除用户!'


@app.route('/_operate_user', methods=['POST'])
@login_required
def _operate_user():
    req_data = json.loads(request.get_data())
    user_name = req_data['user_name']
    staff_id = req_data['staff_id']
    email = req_data['email']
    phone_number = req_data['phone_number']
    operate_type = req_data['operate_type']

    if not g.user.role:
        try:
            if operate_type == 'add':
                if db.session.query(User).filter(User.staff_id == staff_id, User.enable == 0).count():
                    db.session.query(User).filter(User.staff_id == staff_id, User.enable == 0).update(
                        {'user_name': user_name,
                         'email': email,
                         'phone_number': phone_number,
                         'enable': 1,
                         'password': 123456
                         }, synchronize_session='evaluate')
                    db.session.commit()
                    log('system', '解禁用户', -1, user_name, '成功')
                else:
                    if db.session.query(User).filter(
                                                    (User.user_name == user_name) |
                                                    (User.staff_id == staff_id) |
                                            (User.email == email) | (User.phone_number == phone_number)).count():
                        return '姓名、工号、邮箱、手机等信息重复!'
                    new_user = User(user_name, staff_id, email, phone_number)
                    db.session.add(new_user)
                    db.session.commit()
                    log('system', '增加用户', new_user.id, user_name, '成功')
            else:
                user_id = int(req_data['user_id'])
                db.session.query(User).filter(User.id == user_id).update({'user_name': user_name,
                                                                          'staff_id': staff_id,
                                                                          'email': email,
                                                                          'phone_number': phone_number},
                                                                         synchronize_session='evaluate')
                db.session.commit()
                log('system', '增加用户', user_id, user_name, '成功')
            return 'ok'
        except Exception, e:
            print Exception, e
            if operate_type == 'add':
                return '数据库服务异常!'
            else:
                return '更新失败!'
    else:
        return '您无权添加用户!'


@app.route('/_get_user_info', methods=['POST'])
@login_required
def _get_user_info():
    req_data = json.loads(request.get_data())
    try:
        user = User.query.get(int(req_data['user_id'][0]))
        user_info = [{'user_name': user.user_name, 'staff_id': user.staff_id, 'email': user.email,
                      'phone_number': user.phone_number}]
        return jsonify(user=user_info, msg='ok')
    except Exception, e:
        print Exception, e
        return jsonify(msg='获取用户信息失败!')


@app.route('/_modify_password', methods=['POST'])
@login_required
def _modify_password():
    req_data = json.loads(request.get_data())
    old_pwd = req_data['old_pwd']
    new_pwd = req_data['new_pwd']
    try:
        user = db.session.query(User).filter(User.id == g.user.id, User.password == old_pwd).first()
        if user is None:
            return '密码错误!'
        db.session.query(User).filter(User.id == int(g.user.id)).update({'password': new_pwd},
                                                                        synchronize_session='evaluate')
        db.session.commit()
        log('system', '修改密码', user.id, user.user_name, '成功')
        return 'ok'
    except Exception, e:
        print Exception, e
        return '数据库服务异常!'


@app.route('/_get_need_list')
@login_required
def _get_need_list():
    order = request.args.get('order')
    limit = request.args.get('limit')
    offset = request.args.get('offset')
    keyword = request.args.get('keyword')
    project_id = request.args.get('project_id')
    application_id = request.args.get('application_id')
    status = request.args.get('status')
    dive_id = request.args.get('dive_id')

    total_sql = SQL['NEED_TOTAL'].format(keyword, project_id, application_id, status, dive_id)
    total_result = db.engine.execute(total_sql).first()['total']
    list_sql = SQL["NEED_LIST"].format(keyword, project_id, application_id, status, int(offset) * int(limit), limit,
                                       order, dive_id)
    list_result = db.engine.execute(list_sql)
    o = []
    for i in list_result:
        row = {
            "id": i[0],
            "need_name": i[1],
            "sponsor": i[2],
            "itsm_id": i[3],
            "work_load": i[4],
            "charge_person_name": i[5],
            "create_time": i[6][:10],
            "plan_commit_time": i[7],
            "real_commit_time": i[8],
            "status": NEED_STATUS_DICT[i[9]],
            "project_name": i[10],
            "application_name": i[11],
            "need_desc": i[12],
            "sons": i[13]
        }
        o.append(row)
    return jsonify(total=total_result, rows=o)
