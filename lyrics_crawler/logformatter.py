import logging

from scrapy import logformatter


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        # Do not print item when dropping it
        return {
            'level': logging.DEBUG,
            'msg': u"Dropped: %(exception)s",
            'args': {
                'exception': exception
            }
        }
