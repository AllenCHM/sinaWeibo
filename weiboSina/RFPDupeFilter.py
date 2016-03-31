#coding=utf-8
__author__ = 'AllenCHM'

from scrapy.dupefilter import BaseDupeFilter

class MyRFPDupeFilter(BaseDupeFilter):

    @classmethod
    def from_settings(cls, settings):
        return cls()

    @classmethod
    def from_crawler(cls, crawler):
        pass

    def request_seen(self, request):
        pass

    def close(self, reason):
        self.clear()

    def clear(self):
        pass