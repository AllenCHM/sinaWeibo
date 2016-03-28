#coding=utf-8
__author__ = 'AllenCHM'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import codecs
from lxml import etree

items = []
with codecs.open('tmp.html', 'r') as f:
    t = f.read()
    url = re.findall('W_ficon ficon_cd_place S_ficon\\\\"(.*?)<span class=\\\\"item_text W_fl\\\\">(.*?)<\\\\/span>', t, re.S)
    print