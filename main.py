import userencode
import weibosearch
import weiboencode
import weibologin
import weibospider
if __name__ == '__main__':#global main  
    weiboSpider=weibospider.WeiboSpider()
    weiboSpider.SpiderLogin('azhulixing@126.com','654a543')
    #weiboSpider.SpiderSpide('http://weibo.com/u/3131400905',10000)#spide 10000 users
    weiboSpider.SpiderSpide('3131400905',10000)
