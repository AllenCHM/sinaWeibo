#coding=utf-8
__author__ = 'AllenCHM'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import weibologin
import urllib2
import re
import sys,os
import hashlib
import Queue
import time
class WeiboSpider:
    def __init__(self): 
        return None
    
    def SpiderLogin(self, user, pwd, enableProxy = False):#Call interfaces in WeiboLogin to login
        weiboLogin = weibologin.WeiboLogin(user, pwd)#username,password #__init__ constructor
        loginStatus = weiboLogin.Login()
        if loginStatus == True:
            print ("Login Process Success!")
            return True
        else:
            return False
        
    def ParseHtmlConcernsCNumFansFNumUidName(self,htmlUtf8String):
        Concerns=re.search('(href=\\\\")(http:\\\\/\\\\/weibo\\.com\\\\/p\\\\/\\d+\\\\/follow\\?from=.+&mod=headfollow#place\\\\)(" >)'.encode('utf8'),htmlUtf8String)#ret utf8
        if Concerns!=None:
            Concerns=Concerns.group(2)
            Concerns=Concerns.decode('utf8')
            Concerns=re.sub('\\\\','',Concerns)
        CNum=re.search('(\d+)(<\\\\/strong><span class=\\\\"S_txt2\\\\">关注<\\\\/span>)'.decode('gbk').encode('utf8'),htmlUtf8String)#ret utf8
        if CNum!=None:
            CNum=CNum.group(1)
            CNum=CNum.decode('utf8')
        else:
            CNum='0'
        Fans=re.search('(href=\\\\")(http:\\\\/\\\\/weibo\\.com\\\\/p\\\\/\\d+\\\\/follow\\?relate=fans&from=.+&mod=headfans&current=fans#place\\\\)(" >)'.encode('utf8'),htmlUtf8String)
        if Fans!=None:
            Fans=Fans.group(2)
            Fans=Fans.decode('utf8')
            Fans=re.sub('\\\\','',Fans)

        FNum=re.search('(\d+)(<\\\\/strong><span class=\\\\"S_txt2\\\\">粉丝<\\\\/span>)'.decode('gbk').encode('utf8'),htmlUtf8String)#ret utf8
        if FNum!=None:
            FNum=FNum.group(1)
            FNum=FNum.decode('utf8')
        else:
            FNum='0'
        Uid=re.search('(\\$CONFIG\\[\'oid\'\\]=\')(\\d+)(\')'.encode('utf8'),htmlUtf8String).group(2)
        Uid=Uid.decode('utf8')
        Name=re.search('(\\$CONFIG\\[\'onick\'\\]=\')(.+)(\')'.encode('utf8'),htmlUtf8String).group(2)
        Name=Name.decode('utf8')
        
        return Concerns,CNum,Fans,FNum,Uid,Name

    def FindAllUids(self,htmlContent,surfedUid,uidQueue,fp1):
        print('In Find All uids')#action-type=\"follow\" action-data=\"refer_sort=followlist&refer_flag=followlist&uid=
        PatUid=re.compile('(<li class=\\\\"follow_item S_line2\\\\" action-type=\\\\"itemClick\\\\" action-data=\\\\"uid=)(\\d+)'.encode('utf8'))
        for m in PatUid.finditer(htmlContent):
            mUid=m.group(2)
            #print mUid
            if mUid not in surfedUid:
                if uidQueue.put(mUid,True)==Queue.Full:
                    print("The urlQueue is Full,Stop spiding")
                    return
                fp1.write('  '.encode('utf8')+mUid)
        PatNextPage=re.compile('(<a bpfilter=\\\\"page\\\\" class=\\\\"page next S_txt1 S_line1\\\\" href=\\\\")(\\\\/p\\\\/\\d+\\\\/.*)("><span>下一页<\\\\/span><\\\\/a>)'.decode('gbk').encode('utf8'))

        result=PatNextPage.search(htmlContent)

        while result!=None:#存在下一页
            print("Next Page")#系统问题，新浪微博规定只能浏览5页
            
            result=result.group(2)
            result=re.sub('\\\\','',result)
            result='http://weibo.com'+result

            time.sleep(1)
            htmlContent=urllib2.urlopen(result).read()

            PatUid=re.compile('(<li class=\\\\"follow_item S_line2\\\\" action-type=\\\\"itemClick\\\\" action-data=\\\\"uid=)(\\d+)'.encode('utf8'))
            PatUid.search(htmlContent)
            for m in PatUid.finditer(htmlContent):
                #print mUid
                mUid=m.group(2)
                if mUid not in surfedUid:
                    if uidQueue.put(mUid,True)==Queue.Full:
                        print("The urlQueue is Full,Stop spiding")
                        return
                    fp1.write('  '.encode('utf8')+mUid)
            result=PatNextPage.search(htmlContent)
        
    def SpideATime(self,uid4Surf,surfedUid,uidQueue,fp1):
        url4Surf='http://weibo.com/u/'+uid4Surf;
        time.sleep(1)
        htmlResponse=urllib2.urlopen(url4Surf).read()
        Concerns,CNum,Fans,FNum,Uid,Name=self.ParseHtmlConcernsCNumFansFNumUidName(htmlResponse)
        fp1.write(' <newuser>\n'.encode('utf8'))
        fp1.write(' '.encode('utf8')+uid4Surf+'\n'.encode('utf8'))
        if Concerns!=None:
            fp1.write('  <concerns>\n'.encode('utf8'))
            time.sleep(1)
            htmlConcernsUrl=urllib2.urlopen(Concerns).read()
            self.FindAllUids(htmlConcernsUrl,surfedUid,uidQueue,fp1)
            fp1.write('\n  </concerns>\n'.encode('utf8'))
        if Fans!=None:
            fp1.write('  <fans>\n'.encode('utf8'))
            time.sleep(1)
            htmlFansUrl=urllib2.urlopen(Fans).read()
            self.FindAllUids(htmlConcernsUrl,surfedUid,uidQueue,fp1)
            fp1.write('\n  </fans>\n'.encode('utf8'))
        fp1.write(' </newuser>\n'.encode('utf8'))
        return True
    
    def SpiderSpide(self,uidStart,spideNum):
        surfedUid=set()
        #写文件
        os.chdir(os.path.dirname(sys.argv[0]));
        filename1='RelationShip.xml';
        fp1=open(filename1,'wb');
        fp1.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf8'));
        fp1.write('<recipe>\n'.encode('utf8'))
        #写文件
        uidQueue=Queue.Queue(maxsize=spideNum)
        if uidQueue.put(uidStart,True)==Queue.Full:
            print("The urlQueue is Full,Stop spiding")
            return True
        uid4Surf=uidQueue.get_nowait()
        self.SpideATime(uid4Surf,surfedUid,uidQueue,fp1)
        surfedUid.add(uid4Surf)
        
        while uidQueue.empty()==False:
            uid4Surf=uidQueue.get_nowait()
            print(uid4Surf)
            if self.SpideATime(uid4Surf,surfedUid,uidQueue,fp1)==False:
                print('SpiderSpide Error')
                return False
        print('Spiding Ending')
        #写文件
        fp1.write('</recipe>'.encode('utf8'))
        fp1.close()
        #写文件
        return True
        
        
        
