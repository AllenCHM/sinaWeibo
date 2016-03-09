import urllib2
import cookielib
import random
import re
import sys,os
import weiboencode
import weibosearch
class WeiboLogin:
    def __init__(self, user, pwd, enableProxy = False):
        #"initialize WeiboLogin,enableProxy:use proxy server or not,false by acquiescence"
        print("Initializing WeiboLogin...")
        self.userName = user
        self.passWord = pwd
        self.enableProxy = enableProxy

        #self.serverUrl:PreLogin,the following url is found using fiddler after I put in the username and clicked the key submission frame. I found it in the response.
        self.serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.18)&_=1456673156808"
        self.configImgUrl=""
        self.loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

    def GetServerTime(self):
        #"Get server time and nonce, which are used to encode the password"
        print("Getting server time and nonce...")
        serverData = urllib2.urlopen(self.serverUrl).read()#get the page content
        print(serverData)#attention:byte string at present,need a conversion to unicode in python3
        weiboSearch=weibosearch.WeiboSearch()
        try:
            
            serverTime, nonce, pubkey, rsakv = weiboSearch.sServerData(serverData)#parse and get serverTime,nonce
            return serverTime, nonce, pubkey, rsakv
        except:
            print('Get server time & nonce error!')
            return None
    
    def EnableCookie(self, enableProxy):
        #"Enable cookie & proxy (if needed)."        
        cookiejar = cookielib.LWPCookieJar()#construct cookie
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)

        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':'http://xxxxx.pac'})#use proxy
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print ("Proxy enabled")
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)#construct cookie's opener
        
    def Login(self):
        #"login module"  
        self.EnableCookie(self.enableProxy)#cookie configuration or proxy configuration
        
        serverTime, nonce, pubkey, rsakv = self.GetServerTime()#the first step in login
        
        weiboEncode=weiboencode.WeiboEncode()
        
        postData = weiboEncode.PostEncode(self.userName,self.passWord,serverTime,nonce,pubkey,rsakv)#cipher username and password
        print ("Post data length:\n",len(postData))

        req = urllib2.Request(self.loginUrl, postData, self.postHeader)#urllib2 carries a cookie from now on 
        
        print ("Posting request...")
        result=urllib2.urlopen(req)#second step
        text = result.read()
        #print('-----the text is----:',text)
        q=re.compile('"retcode":0,"arrURL":')#notice:"retcode":0,"arrURL" indicates success.Why not using 'Set-Cookie:Cookie'?As it isn't in htmlcontent
        matched=q.search(text)
        if matched==None:
            print('Login False,Step: Login Request')
            matched2=re.search('&retcode=4049&',text)
            if matched2!=None:#indicated from login success login false.Sina judge whether needing verification code after typing in the username sometimes,while always judging whether needing verification code after pust'commit'
                print('Reason: Please Type in your Verification Code(see the .png in the current directory)')
                iRand=str(random.randint(100000000,999999999))
                verifyUrl='http://login.sina.com.cn/cgi/pin.php?r=' + iRand + '&s=0'
                responseImg=urllib2.urlopen(verifyUrl).read()
                os.chdir(os.path.dirname(sys.argv[0]))
                oFile=open('verifyImg.png','wb')
                oFile.write(responseImg);
                oFile.close()
                VerificationCode=raw_input('Type in the Code here:')
                postData = weiboEncode.VerificationCodePostEncode(self.userName,self.passWord,serverTime,nonce,pubkey,rsakv,VerificationCode)
                print ("Post data length:\n",len(postData))
                req = urllib2.Request(self.loginUrl, postData, self.postHeader)
                print ("Posting request...")
                result=urllib2.urlopen(req)
                text = result.read()           
        try:
            weiboSearch=weibosearch.WeiboSearch()
            loginUrl = weiboSearch.sRedirectData(text)#Redirect the result,Attention:using weiboSearch
            htmlResponse=urllib2.urlopen(loginUrl).read()

            p=re.compile('src="/js/visitor/mini.js"')
            matched=p.search(htmlResponse)
            if matched!=None:
                print('Login False,Step:sRedirectData')
            else:
                print('Login Success,Step:sRedirectData')
        except:
            print ('Login Process error!')
            return False   
        print ('Login Process sucess!')
        return True
