# -*- coding:utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

DOWNLOAD_DIRECTORY = os.path.join(basedir, 'tmp')
PROJECT_STATUS = [('1', '意向'), ('2', '在建'), ('3', '结项')]
APPLICATION_STATUS = [('1', '活跃'), ('2', '沉默')]
TASK_STATUS = {1: '未开始', 2: '执行中', 3: '已暂停', 4: '已作废', 5: '已完成'}
TASK_STATUS_LIST = [(1, '未开始'), (2, '执行中'), (3, '已暂停'), (4, '已作废'), (5, '已完成')]
EXPERIENCE_TYPE_DICT = {1: '知识心得', 2: '部署维护', 3: '问题处理'}
EXPERIENCE_TYPE_LIST = [(1, '知识心得'), (2, '部署维护'), (3, '问题处理')]
USER_ROLE_LIST = [(0, '管理员'), (1, '项目经理'), (2, '产品经理'), (3, '团队成员'), (4, '外部人员')]
NEED_STATUS_LIST = [(1, '待对接'), (2, '待分析'), (3, '待设计'), (4, '待实现'), (5, '待发布'), (6, '已完结')]
NEED_STATUS_DICT = {1: '待对接', 2: '待分析', 3: '待设计', 4: '待实现', 5: '待发布', 6: '已完结'}
