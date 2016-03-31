#coding=utf-8
__author__ = 'AllenCHM'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import re
import json
import sys,os
class WeiboSearch:
    def __init__(self):
        return None
    
    def sServerData(self,serverData):
        print(serverData)
        p = re.compile('\((.*)\)')
        jsonData = p.search(serverData).group(1)
        data = json.loads(jsonData)
        
        
        serverTime = str(data['servertime'])
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']
        print ("Server time is:", serverTime)
        print ("Nonce is:", nonce)
        return serverTime, nonce, pubkey, rsakv

    def sRedirectData(self,text):
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        loginUrl = p.search(text).group(1)
        print ('loginUrl:',loginUrl)
        return loginUrl
