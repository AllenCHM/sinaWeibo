#coding=utf-8
__author__ = 'AllenCHM'

#coding=utf-8
__author__ = 'AllenCHM'


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import sys,os
import urllib2
import base64
import rsa
import binascii
def GetUserName(userName):
    "Used to encode user name"
    userNameTemp = urllib2.quote(userName)
    userNameEncoded = base64.encodestring(userNameTemp)[:-1]
    return userNameEncoded

def get_pwd(password, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey,65537)#create public key
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)#create clear text
    passwd = rsa.encrypt(message, key)#cipher text
    passwd = binascii.b2a_hex(passwd)#convert the cipher text into hexadecimal
    return passwd
