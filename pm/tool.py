# -*- coding:utf-8 -*-
import types, time, os
from pyExcelerator import *
from config import DOWNLOAD_DIRECTORY
from flask import g
from models import Log
from pm import db

def clean(data):
    file_name = DOWNLOAD_DIRECTORY + "/" + data + ".xls"
    os.remove(file_name)
    return 'ok'


def genxls(header, data):
    wb = Workbook()
    ws = wb.add_sheet(u'结果')
    # style = XFStyle()
    # style.font.bold = True
    # style.font.colour_index = 13
    # style.font.height = 240
    for i in range(len(header)):
        # ws.write(0, i, header[i], style)
        ws.write(0, i, header[i])
    for i in range(len(data)):
        for j in range(len(data[i])):
            ws.write(i + 1, j, nvl(data[i][j]))
    file_name = DOWNLOAD_DIRECTORY + "/" + str(g.user.id) + str(time.time()).split('.')[0] + ".xls"
    wb.save(file_name)
    return str(g.user.id) + str(time.time()).split('.')[0]


def nvl(a, b=''):
    if type(a) is types.ListType:
        counter = 0
        for i in a:
            if i is None:
                a[counter] = b
            counter += 1
        return a
    if a is None:
        return b
    return a


def join(a):
    counter = 0
    for i in a:
        if i is None:
            a[counter] = '0'
            continue
        a[counter] = str(i)
        counter += 1
    return ','.join(a)


def log(model,action,obj_id,obj_name,detail):
    new_log = Log(model,action,obj_id,obj_name,detail,g.user.id,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    db.session.add(new_log)
    db.session.commit()
    return True
