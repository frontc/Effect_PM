# -*- coding:utf-8 -*-

SQL = {
    "PROJECT_INFO": "select project.project_name as project_name, \
user.user_name as project_manager_name, \
project.build_year as build_year, \
(case project.status when 1 then '意向' when 2 then '在建' when 3 then '结项' end) as status \
    from project,user where project.project_manager_id = user.id",
    "APPLICATION_INFO": "select application.application_name as application_name, \
user.user_name as product_manager_name, \
application.current_version as current_version, \
(case application.status when 1 then '活跃' when 2 then '沉默' end) as status \
    from application,user where application.product_manager_id = user.id",
    "NEED_LIST_DESC": "select need_name,\
case when length(need_desc) = length(left(need_desc,30)) then need_desc \
else concat(left(need_desc,30),'...') END as need_desc \
from need order by create_time DESC limit 8",
    "NEED_LIST_BY_KEYWORD": "select need_name,\
  case when length(need_desc) = length(left(need_desc,30)) then need_desc \
  else concat(left(need_desc,30),'...') END as need_desc \
  from (\
  select need_name,\
  need_desc,\
  concat((select user_name from user where user.id=need.create_person_id),(select user_name from user where user.id=need.charge_person_id)) user_name,\
  create_time \
from need) a \
where need_name like '%%{0}%%' or need_desc like '%%{0}%%' or user_name like '%%{0}%%' \
order by create_time DESC limit 8",
    "NEEDS": "select id,need_name,outer_sponsor,inner_sponsor,itsm_id,\
(select project_name from project where need.project_id=project.id) project_name,\
(select application_name from application where need.application_id=application.id) application_name,\
(select user_name from user where need.create_person_id=user.id) create_person_name,\
(select user_name from user where need.charge_person_id=user.id) charge_person_name,\
date_format(create_time,'%%Y-%%m-%%d') create_time,plan_commit_time,real_commit_time,\
case status when 1 then '待对接' when 2 then '待分析' when 3 then '待设计' when 4 then '待实现' when 5 then '待发布' when 6 then '已完结' else '未知' end status,\
(select count(1) from need b where b.parent_need_id=need.id) sons,work_load \
from need need \
where level_id = 1",
    "NEEDS_SONS": "select id,need_name,outer_sponsor,inner_sponsor,itsm_id,\
(select project_name from project where need.project_id=project.id) project_name,\
(select application_name from application where need.application_id=application.id) application_name,\
(select user_name from user where need.create_person_id=user.id) create_person_name,\
(select user_name from user where need.charge_person_id=user.id) charge_person_name,\
date_format(create_time,'%%Y-%%m-%%d') create_time,plan_commit_time,real_commit_time,\
case status when 1 then '待对接' when 2 then '待分析' when 3 then '待设计' when 4 then '待实现' when 5 then '待发布' when 6 then '已完结' else '未知' end status,\
(select count(1) from need b where b.parent_need_id=need.id) sons,work_load \
from need need \
where level_id = 2 and parent_need_id={0}",
    "NEED_DETAIL": "select id,need_name,need_desc, \
(select project_name from project where need.project_id=project.id) project_name,\
(select application_name from application where need.application_id=application.id) application_name,(select user_name from user where need.create_person_id=user.id) create_person_name,work_load from need where id = {0}",
    "TASK_LIST": "SELECT id,stage_name,task_name,task_detail,\
  (SELECT user_name \
   FROM pm.user \
   WHERE user.id = task.charge_person_id)      charge_person_name,\
  (SELECT user_name \
   FROM pm.user \
   WHERE user.id = task.partner_person_id)     partner_person_name,\
  plan_start_time,\
  plan_finish_time,\
  real_start_time,\
  real_finish_time,\
  processing_progress,\
  CASE status \
  WHEN 1 \
    THEN '未开始' \
  WHEN 2 \
    THEN '执行中' \
  WHEN 3 \
    THEN '已暂停' \
  WHEN 4 \
    THEN '已作废' \
  WHEN 5 \
    THEN '已完成' \
  ELSE '未知' END                                status,\
  comment,\
  (SELECT need_name \
   FROM pm.need \
   WHERE need.id = task.need_id)         need_name \
FROM pm.task {0}",
    "NEW_TASK": "INSERT INTO task(stage_name,task_name,task_detail,charge_person_id,plan_start_time,plan_finish_time,real_start_time,real_finish_time,processing_progress,status,comment,need_id,create_person_id,create_time)\
 VALUES('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}')",
    "UPDATE_TASK": "update task set \
stage_name='{0}',task_name='{1}',task_detail='{2}',charge_person_id='{3}',\
plan_start_time='{4}',plan_finish_time='{5}',real_start_time='{6}',real_finish_time='{7}',\
processing_progress='{8}',status='{9}',comment='{10}',need_id='{11}',modify_person_id='{12}',modify_time='{13}',commit_time='{14}' \
 where id={15}",
    "DELETE_TASK": "delete from task where id in ({0})",
    "ACTIVITY_LIST": ''' SELECT concat(
           (CASE WHEN time_diff < 5
             THEN '刚刚'
            WHEN time_diff < 10
              THEN '五分钟前'
            WHEN time_diff < 30
              THEN '十分钟前'
            WHEN time_diff < 60
              THEN '半小时前'
            WHEN time_diff < 120
              THEN '一小时前'
            WHEN time_diff < 480
              THEN '四小时前'
            WHEN time_diff < 2880
              THEN '一天前'
            WHEN time_diff < 4320
              THEN '两天前'
            WHEN time_diff < 26160
              THEN '一星期前'
            ELSE '很久以前' END), ' ', user_name, ' ', action, ' [', obj_name, '] ', obj_type) active_desc
FROM (SELECT log_time,TIMESTAMPDIFF(MINUTE, log_time, now()) time_diff,
        (SELECT user_name FROM user WHERE user.id = log.user_id) user_name,
        CASE action WHEN '修改项目' THEN '修改了' WHEN '增加项目' THEN '增加了' END action,
        obj_name,'项目' obj_type
      FROM log
      WHERE model = 'project' AND log.obj_id IN (SELECT id FROM project WHERE project_manager_id = {0})
      UNION
      SELECT
        log_time,
        TIMESTAMPDIFF(MINUTE, log_time, now()) time_diff,
        (SELECT user_name
         FROM user
         WHERE user.id = log.user_id)          user_name,
        CASE action
        WHEN '修改系统'
          THEN '修改了'
        WHEN '增加系统'
          THEN '增加了' END                       action,
        obj_name,
        '系统'                                   obj_type
      FROM log
      WHERE model = 'application' AND log.obj_id IN (SELECT id
                                                     FROM application
                                                     WHERE product_manager_id = {0})
      UNION
      SELECT
        log_time,
        TIMESTAMPDIFF(MINUTE, log_time, now()) time_diff,
        (SELECT user_name
         FROM user
         WHERE user.id = log.user_id)          user_name,
        CASE action
        WHEN '修改需求'
          THEN '修改了'
        WHEN '增加需求'
          THEN '增加了' END                       action,
        obj_name,
        '需求'                                   obj_type
      FROM log
      WHERE model = 'need' AND log.obj_id IN (SELECT id
                                              FROM need
                                              WHERE charge_person_id = {0}
                                              OR
                                                                                      need.application_id IN (SELECT id
                                                                                                              FROM
                                                                                                                application
                                                                                                              WHERE
                                                                                                                product_manager_id
                                                                                                                = {0})
                                                                                      OR need.project_id IN (SELECT id
                                                                                                             FROM
                                                                                                               project
                                                                                                             WHERE
                                                                                                               project_manager_id
                                                                                                               = {0}))
      UNION
      SELECT
        log_time,
        TIMESTAMPDIFF(MINUTE, log_time, now()) time_diff,
        (SELECT user_name
         FROM user
         WHERE user.id = log.user_id)          user_name,
        CASE action
        WHEN '更新任务'
          THEN '更新了'
        WHEN '修改任务'
          THEN '修改了'
        WHEN '增加任务'
          THEN '增加了'
        WHEN ' 删除任务'
          THEN '删除了' END                       action,
        obj_name,
        '任务'                                   obj_type
      FROM log
      WHERE model = 'task' AND log.obj_id IN (SELECT id
                                              FROM task
                                              WHERE charge_person_id = 1 OR task.need_id
                                                                            IN (SELECT id
                                                                                FROM need
                                                                                WHERE charge_person_id = {0}
                                                                                      OR
                                                                                      need.application_id IN (SELECT id
                                                                                                              FROM
                                                                                                                application
                                                                                                              WHERE
                                                                                                                product_manager_id
                                                                                                                = {0})
                                                                                      OR need.project_id IN (SELECT id
                                                                                                             FROM
                                                                                                               project
                                                                                                             WHERE
                                                                                                               project_manager_id
                                                                                                               = {0}))
      )
      UNION
      SELECT
        log_time,
        TIMESTAMPDIFF(MINUTE, log_time, now()) time_diff,
        (SELECT user_name FROM user WHERE user.id = log.user_id) user_name,
        CASE action
        WHEN '增加知识'
          THEN '分享了'
        WHEN '修改知识'
          THEN '修改了'
        WHEN '删除知识'
          THEN '删除了' END   action,
        obj_name,
        '心得'                                   obj_type
      FROM log
      WHERE model = 'experience'
      ) a
ORDER BY a.log_time DESC''',
    "EXPERIENCE_TOTAL": "SELECT count(*) total \
FROM experience \
WHERE experience.title LIKE '%%{0}%%' OR \
      experience.summary LIKE '%%{0}%%' OR \
      experience.detail LIKE '%%{0}%%' OR \
      experience.related_application_id in(select id from application where application_name like '%%{0}%%') OR \
      experience.related_project_id in (select id from project where project_name like '%%{0}%%')",
    "EXPERIENCE_LIST": "SELECT id,title,summary,type,\
(select project_name from project where project.id = related_project_id) related_project_name,\
(select application_name from application where application.id=related_application_id) related_application_name,\
(select user_name from user where user.id=modify_person_id) modify_person_name,modify_time \
FROM experience \
WHERE experience.title LIKE '%%{0}%%' OR \
      experience.summary LIKE '%%{0}%%' OR \
      experience.detail LIKE '%%{0}%%' OR \
      experience.related_application_id in(select id from application where application_name like '%%{0}%%') OR \
      experience.related_project_id in (select id from project where project_name like '%%{0}%%') \
      ORDER BY modify_time DESC \
      limit {1},{2}",
    "EXP_LIST": "select id,title,url,summary,\
  (select user_name from user where user.id=modify_person_id) user,\
  date_format(modify_time,'%%Y-%%m-%%d') modify_time,type \
from experience order by modify_time DESC"
}
