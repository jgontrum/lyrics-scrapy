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
            raise DropItem(
                "{artist}: {title} - Lyrics too short: '{lyrics}'".format
                (**item))
        elif "Lyrics currently unavailable" in item['lyrics']:
            raise DropItem(
                "{artist}: {title} - Lyrics not available".format(**item))

        language = langid.classify(item['lyrics'])
        item['language'] = language[0]

        item['artist'] = item['artist'].strip()
        item['album'] = item['album'].strip()
        item['title'] = item['title'].strip()
        item['lyrics'] = item['lyrics'].strip()

        return item
