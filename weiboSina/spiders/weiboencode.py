#coding=utf-8
__author__ = 'AllenCHM'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import urllib
import base64
import binascii
import userencode
class WeiboEncode:#the member function in python3 can't begin with self,otherwise the first param will be treated as a normal param,while python2 member function must begin with self,although not filt in when called,the compile will put in the param in secret
    def __init__(self):
        return None
    
    def PostEncode(self,userName, passWord, serverTime, nonce, pubkey, rsakv):
        "Used to generate POST data"
        encodedUserName = userencode.GetUserName(userName)#username encryped by base64
        encodedPassWord = userencode.get_pwd(passWord, serverTime, nonce, pubkey)#cyrrently password encryped by rsa
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
            'servertime': serverTime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': encodedPassWord,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': rsakv,     
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postData = urllib.urlencode(postPara)#network encrypt
        return postData

    #PostData with verification code
    def VerificationCodePostEncode(self,userName, passWord, serverTime, nonce, pubkey, rsakv,verificationCode):
        encodedUserName = userencode.GetUserName(userName)#username encryped by base64
        encodedPassWord = userencode.get_pwd(passWord, serverTime, nonce, pubkey)#cyrrently password encryped by rsa
        postPara = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'door':verificationCode,
            'vsnf': '1',
            'vsnval': '',
            'su': encodedUserName,
            'service': 'miniblog',
            'servertime': serverTime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': encodedPassWord,
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': rsakv,     
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }
        postData = urllib.urlencode(postPara)   
        return postData
