# -*- coding:utf-8 -*-
import sys
import pymysql
reload(sys)
sys.setdefaultencoding('utf8')

db = pymysql.connect(host='localhost',user='root',passwd='odsods',db='pm',charset='utf8')
cu = db.cursor()
cu.execute("delete from user")
db.commit()
for row in [('方超','d2814','fangchao@tydic.com','15375346803','ods','0','1'),('朱丙省','d0924','zhubs@tydic.com','15375346803','123456','1','1')]:
    #print("insert into user (user_name,staff_id,email,phone_number,password,role) values('{0}','{1}','{2}','{3}','{4}')".format(*row))
    cu.execute("insert into user (user_name,staff_id,email,phone_number,password,role,enable) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(*row))
db.commit()
print cu.execute("select * from user")
cu.close()
db.close()