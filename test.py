
import pymysql

import logging

usersvalues = []

usersvalues.append(("chinese_district", "chinese_area", "xiaoqu", "layout", "22", "11"))  # 注意要用两个括号扩起来
usersvalues.append(("chinese_district", "chinese_area", "xiaoqu", "layout", "33", "22"))
print(usersvalues)
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='123456', database='lianjia', charset='utf8')
cursor = db.cursor()
sql = "INSERT INTO zufang(district, area, xiaoqu, layout, size, price) VALUES (%s,%s,%s,%s,%s,%s)"
try:
    # 执行sql语句
    cursor.executemany(sql,usersvalues)
    # 提交到数据库执行
    db.commit()
except Exception as e:
    # 如果发生错误则回滚
    logging.exception(e)
    db.rollback()

# 关闭数据库连接
db.close()