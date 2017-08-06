# -*- coding:utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = 'fangchao'
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:odsods@localhost/pm"  # 数据库链接传
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True
