# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class WeibosinaPipeline(object):
    def __init__(self, HOST, USERNAME, PASSWORD, DBNAME):
        self.mysqlConn = pymysql.connect(host=HOST, user=USERNAME, passwd=PASSWORD, db=DBNAME, port=3306, charset='utf8')
        self.cur = self.mysqlConn.cursor()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        HOST = crawler.settings.get(u'HOST')
        USERNAME = crawler.settings.get(u'USERNAME')
        PASSWORD = crawler.settings.get(u'PASSWORD')
        DBNAME = crawler.settings.get(u'DBNAME')
        return cls(HOST, USERNAME, PASSWORD, DBNAME)


    def process_item(self, item, spider):
        self.cur.execute('select uid from weibo WHERE  uid = {uid}'.format(uid=item[u'uid']))

        t = self.cur.fetchall()
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

        self.cur.execute(sentence)

        return item

    def closed(self, reason):
        self.cur.close()
        self.mysqlConn.commit()

