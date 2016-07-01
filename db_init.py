# -*- coding:utf-8 -*-
import sys
import pymysql
reload(sys)
sys.setdefaultencoding('utf8')

db = pymysql.connect(host='ubuntu1',user='root',passwd='ods',db='pm',charset='utf8')
cu = db.cursor()
cu.execute("delete from user")
db.commit()
for row in [('方超','d2814','fangchao@tydic.com','18956060302','ods',0),('朱丙省','d0924','zhubs@tydic.com','15375346803','123456',1)]:
    cu.execute("insert into user (user_name,staff_id,email,phone_number,password,role) values(?,?,?,?,?,?)", row)
db.commit()
print cu.execute("select * from user").fetchall()
cu.close()
db.close()