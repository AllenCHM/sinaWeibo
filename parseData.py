#coding=utf-8
__author__ = 'AllenCHM'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import csv
import pymysql


HOST = u'192.168.2.247'
USERNAME=u'root'
PASSWORD=u'000000'
DBNAME=u'Weibo'

mysqlConn = pymysql.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DBNAME, port=3306, charset='utf8')
cur = mysqlConn.cursor()


reader = csv.DictReader(open('test.csv',"rb"),quoting=csv.QUOTE_ALL)

for item in reader:
    for i in item.keys():
        item[i] = item[i].decode(u'utf-8', errors=u'ignore')

    cur.execute('select uid from weibo WHERE  uid = {uid}'.format(uid=item[u'uid']))
    t = cur.fetchall()
    if not t or not t[0]:
        sentence = '''
            INSERT INTO weibo (uid, sex, place, school, profile, weiboText)
                  VALUES ('{uid}', '{sex}', '{place}', '{school}', '{profile}', '{weiboText}');
        '''.format(uid=item[u'uid'], sex=item[u'sex'], place=item[u'place'], school=item[u'school'], profile=item[u'profile'], weiboText=item[u'weiboText'], )
    else:
        try:
            sentence = '''update weibo SET uid='{uid}', sex='{sex}', place='{place}', school='{school}', profile='{profile}', weiboText='{weiboText}'WHERE uid='{uid}'
            '''.format(uid=item[u'uid'], sex=item[u'sex'], place=item[u'place'], school=item[u'school'], profile=item[u'profile'], weiboText=item[u'weiboText'], )
        except:
            print u'error exit'
            exit()
    try:
        cur.execute(sentence)
        mysqlConn.commit()
    except Exception, e:
        pass

cur.close()
mysqlConn.close()
