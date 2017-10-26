# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LyricsCrawlerItem(scrapy.Item):
    artist = scrapy.Field()
    artist_id = scrapy.Field()
    artist_popularity = scrapy.Field()
    album = scrapy.Field()
    title = scrapy.Field()
    song_id = scrapy.Field()
    language = scrapy.Field()
    lyrics = scrapy.Field()
    year = scrapy.Field()
    valid = scrapy.Field()
