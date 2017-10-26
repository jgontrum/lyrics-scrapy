# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import langid


class LyricsCrawlerPipeline(object):
    def process_item(self, item, spider):
        item['lyrics'] = "\n".join([
            v.strip() for v in item['lyrics'] if v.strip()
        ])

        if len(item['lyrics']) < 10 or \
                        "Lyrics currently unavailable" in item['lyrics']:
            item['valid'] = False
        else:
            item['valid'] = True

        language = langid.classify(item['lyrics'])
        item['language'] = language[0]

        item['artist'] = item['artist'].strip()
        item['album'] = item['album'].strip()
        item['title'] = item['title'].strip()
        item['lyrics'] = item['lyrics'].strip()

        return item
