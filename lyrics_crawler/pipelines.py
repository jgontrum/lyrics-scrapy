# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import langid
from scrapy.exceptions import DropItem


class LyricsCrawlerPipeline(object):
    def process_item(self, item, spider):
        item['lyrics'] = "\n".join([
            v.strip() for v in item['lyrics'] if v.strip()
        ])

        if len(item['lyrics']) < 10:
            raise DropItem("Lyrics too short %s" % item)
        elif "Lyrics currently unavailable" in item['lyrics']:
            raise DropItem("Lyrics not available %s" % item)

        language = langid.classify(item['lyrics'])
        item['language'] = language[0]

        return item
