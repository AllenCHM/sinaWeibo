#coding=utf-8
__author__ = 'AllenCHM'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import userencode
import weibosearch
import weiboencode
import weibologin
import weibospider
if __name__ == '__main__':#global main
    weiboSpider=weibospider.WeiboSpider()
    weiboSpider.SpiderLogin('15607966477','a123456')
    #weiboSpider.SpiderSpide('http://weibo.com/u/3131400905',10000)#spide 10000 users
    weiboSpider.SpiderSpide('1263317424',10)
