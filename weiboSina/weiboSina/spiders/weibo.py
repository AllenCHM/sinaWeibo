#coding=utf-8
__author__ = 'AllenCHM'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from scrapy.http import Request, FormRequest
from scrapy.spider import Spider
from scrapy.selector import Selector

import re
import urllib2
import urllib
import random
from lxml import etree
import time

import weibosearch
import cookielib
import weiboencode
import userencode

from weiboSina.items import WeibosinaItem


class WeiBoSpider(Spider):
    name = u'weibo'

    def __init__(self, userid, passwd):
        self.userName = userid
        self.passWord = passwd

        self.serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_={timestamp}".format(timestamp=int(time.time()*1000))
        self.configImgUrl=""
        self.loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        userName = crawler.settings.get(u'USERNAME')
        passwd = crawler.settings.get(u'PASSWD')
        return cls(userName, passwd)

    def start_requests(self):
        print("Getting server time and nonce...")
        yield Request(self.serverUrl, meta={u'cookiejar':1}, callback=self.GetServerTime)

    def GetServerTime(self, response):
        serverData = response.body
        print(serverData)#attention:byte string at present,need a conversion to unicode in python3
        weiboSearch=weibosearch.WeiboSearch()
        try:
            self.serverTime, self.nonce, self.pubkey, self.rsakv = weiboSearch.sServerData(serverData)#parse and get serverTime,nonce
            encodedUserName = userencode.GetUserName(self.userName)#username encryped by base64
            encodedPassWord = userencode.get_pwd(self.passWord, self.serverTime, self.nonce, self.pubkey)#cyrrently password encryped by rsa
            postPara = {
                'entry': 'weibo',
                'gateway': '1',
                'from': '',
                'savestate': '7',
                'userticket': '1',
                'ssosimplelogin': '1',
                'vsnf': '1',
                'vsnval': '',
                'su': encodedUserName,
                'service': 'miniblog',
                'servertime': self.serverTime,
                'nonce': self.nonce,
                'pwencode': 'rsa2',
                'sp': encodedPassWord,
                'encoding': 'UTF-8',
                'prelt': '132',
                'rsakv': self.rsakv,
                'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                'returntype': 'META'
            }
            postData = urllib.urlencode(postPara) #network encrypt
            yield Request(self.loginUrl+u'&'+postData, meta={u'cookiejar':response.meta[u'cookiejar']}, headers=self.postHeader, callback=self.getV)
        except:
            print('Get server time & nonce error!')
            return

    def getV(self, response):
        q=re.compile('"retcode":0,"arrURL":')#notice:"retcode":0,"arrURL" indicates success.Why not using 'Set-Cookie:Cookie'?As it isn't in htmlcontent
        matched=q.search(response.body)
        if matched==None:
            print('Login False,Step: Login Request')
            matched2=re.search('&retcode=4049&',response.body)
            if matched2!=None:#indicated from login success login false.Sina judge whether needing verification code after typing in the username sometimes,while always judging whether needing verification code after pust'commit'
                print('Reason: Please Type in your Verification Code(see the .png in the current directory)')
                iRand=str(random.randint(100000000,999999999))
                verifyUrl='http://login.sina.com.cn/cgi/pin.php?r=' + iRand + '&s=0'
                yield Request(verifyUrl, meta={u'cookiejar':response.meta[u'cookiejar']}, callback=self.parseV)
        try:
            weiboSearch=weibosearch.WeiboSearch()
            loginUrl = weiboSearch.sRedirectData(response.body)#Redirect the result,Attention:using weiboSearch
            yield Request(loginUrl, meta={u'cookiejar':response.meta[u'cookiejar']}, callback=self.parse)
        except:
            print ('Login Process error!')
            return
        print ('Login Process sucess!')
        return

    def parseV(self, response):
        oFile=open('./verifyImg.png','wb')
        oFile.write(response.body);
        oFile.close()
        VerificationCode=raw_input('Type in the Code here:')
        encodedUserName = userencode.GetUserName(self.userName)#username encryped by base64
        encodedPassWord = userencode.get_pwd(self.passWord, self.serverTime, self.nonce, self.pubkey)#cyrrently password encryped by rsa
        postPara = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'door':VerificationCode,
            'vsnf': '1',
            'vsnval': '',
            'su': encodedUserName,
            'service': 'miniblog',
            'servertime': self.serverTime,
            'nonce': self.nonce,
            'pwencode': 'rsa2',
            'sp': encodedPassWord,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv':self. rsakv,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postData = urllib.urlencode(postPara)
        print ("Post data length:\n",len(postData))
        yield Request(self.loginUrl+u'&'+postData, meta={u'cookiejar':response.meta[u'cookiejar']}, headers=self.postHeader, callback=self.getV)

    def parse(self, response):
        p=re.compile('src="/js/visitor/mini.js"')
        matched=p.search(response.body)
        if matched!=None:
            print('Login False,Step:sRedirectData')
            return
        else:
            print('Login Success,Step:sRedirectData')
            name = re.findall(u'"userinfo":\{"uniqueid":"(.*?)"', response.body, re.S)
            if name:
                #获取首页
                url = u'http://weibo.com/{name}'.format(name=name[0])
                item = {}
                item[u'id'] = name[0]
                yield Request(url, meta={u'cookiejar':response.meta[u'cookiejar'], u'item':item}, callback=self.getIndexPageUrl)

                #获取关注页
                # url = u'http://weibo.com/{name}/follow'.format(name=name)
                # yield Request(url, meta={u'cookiejar':response.meta[u'cookiejar']}, callback=self.parseFollow)
            else:
                print u'get uid error'
                return

    def getIndexPageUrl(self, response):
        url = u'http://weibo.com/' + re.findall('\$CONFIG\[\'watermark\'\]=\'(.*?)\'', response.body, re.S)[0] + u'?is_all=1'
        yield Request(url, meta={u'cookiejar':response.meta[u'cookiejar'], u'item':response.meta[u'item'],}, dont_filter=True, callback=self.parseIndex)

    def parseFollow(self, response):
        lis = re.findall(u'(<li class=\\\\"member_li S_bg1\\\\" node-type=\\\\"user_item\\\\".*?/li>)', response.body, re.S)
        for li in lis:
            item = {}
            item[u'id'] = re.findall('usercard=\\\\"id=(\d*?)\\\\" >', li, re.S)[0]
            item[u'userName'] = re.findall('title=\\\\"(.*?)\\\\" usercard=\\\\"', li, re.S)[0]
            item[u'url'] = re.findall('node-type=\\\\"screen_name\\\\"  href=\\\\"\\\\(.*?)\\\\" class=', li, re.S)[0]
            yield Request(u'http://weibo.com'+item[u'url'], meta={u'cookiejar':response.meta[u'cookiejar'], u'item':item}, callback=self.parseIndex)

        nextPage = re.findall('class=\\\\"page next S_txt1 S_line1\\\\" href=\\\\"(.*?)"><span>下一页<', response.body, re.S)
        if nextPage:
            url = u'http://weibo.com' + nextPage[0]
            yield Request(url,  meta={u'cookiejar':response.meta[u'cookiejar']}, callback=self.parseFollow)

    def parseIndex(self, response):
        item = WeibosinaItem()
        item[u'uid'] = response.meta[u'item'][u'id']
        try:
            item[u'place'] = re.findall('W_ficon ficon_cd_place S_ficon\\\\"(.*?)<span class=\\\\"item_text W_fl\\\\">(.*?)<\\\\/span>', response.body, re.S)[0][1].replace('\\r', '').replace('\\n', '').replace('\\t', '').strip()
        except:
            item[u'place'] = None
        try:
            item[u'school']  = re.findall('毕业于<\\\\/span>(.*?)<a target=\\\\"_blank\\\\" (.*?)>(.*?)<\\\\/a>', response.body, re.S)[0][2]
        except:
            item[u'school'] = None
        try:
            item[u'profile']  = re.findall('class=\\\\"pf_intro\\\\" title=\\\\"(.*?)\\\\">', response.body, re.S)[0]
        except:
            item[u'profile'] = None
        try:
            item[u'sex']  = re.findall('<span class=\\\\"icon_bed\\\\"><a><i class=\\\\"W_icon icon_pf_(.*?)\\\\"><\\\\/i>', response.body, re.S)[0]
        except:
            item[u'sex'] = None
        try:
            weiboText = re.findall('(<div class=\\\\"WB_text W_f14\\\\" node-type=\\\\"feed_list_content\\\\" .*?<\\\\/div>)', response.body, re.S)[0]
            weiboText = weiboText.replace('\\"', '"').replace('\\n', '').replace('\\/', '/')
            weiboText = etree.HTML(weiboText.decode(u'utf-8'))
            item[u'weiboText'] = weiboText.xpath('string(.)').strip().replace(' ', '')
        except:
            item[u'weiboText'] = None
        yield item
        print

        url = re.findall('a bpfilter=\\\\"page_frame\\\\"  class=\\\\"t_link S_txt1\\\\" href=\\\\"(.*?)" ><strong class=(.*?)\\\\/strong><span class=\\\\"S_txt2\\\\">关注<\\\\/span>', response.body, re.S)
        try:
            url = url[0][0].replace('\\/', '/').replace('\\', '')
            yield Request(url, meta={u'cookiejar':response.meta[u'cookiejar']}, callback=self.parseFollow)
        except:
            print u'can\'t get {uid}\'s followers'.format(uid=response.meta[u'item'][u'uid'])







































            # return serverTime, nonce, pubkey, rsakv
        # except:
        #     print('Get server time & nonce error!')
        #     return None

    #     loginStatus = self.login()
    #     if loginStatus == True:
    #         print ("Login Process Success!")
    #     else:
    #         exit(u'登陆失败')

