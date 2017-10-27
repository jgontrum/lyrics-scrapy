# -*- coding: utf-8 -*-
import re

import scrapy

from lyrics_crawler.items import LyricsCrawlerItem

ALBUM_YEAR_REGEX = re.compile(r"\((\d+)\)$", flags=re.UNICODE)


class WikiaSpider(scrapy.Spider):
    name = 'Wikia.com'
    allowed_domains = ['lyrics.wikia.com']
    start_urls = [
        'http://lyrics.wikia.com/wiki/Category:Artists_by_First_Letter']

    def _song(self, response):
        self.logger.debug("Current song page: {}".format(response.url))

        meta = {
            "title": response.meta['title'],
            "artist": response.meta['artist']
        }

        # Try to find album name
        album_name = response.xpath(
            '//div[contains(@id, "song-header-container")]'
            '/p'
            '/i'
            '/a'
            '/text()'
        ).extract_first()

        if album_name:
            # Get year and remove it from album title
            year = ALBUM_YEAR_REGEX.findall(album_name)
            if year:
                meta["year"] = int(year[0])

            meta["album"] = ALBUM_YEAR_REGEX.sub("", album_name).strip()

        # Get lyrics
        lyrics = response.xpath(
            '//div[contains(@class, "lyricbox")]//text()').extract()

        meta['song_id'] = response.url.replace(
            "http://lyrics.wikia.com/wiki/", "")

        meta['lyrics'] = lyrics

        yield LyricsCrawlerItem(meta)

    def _artist(self, response):
        self.logger.debug("Current artist page: {}".format(response.url))

        artist_name = response.xpath(
            '//header[contains(@id, "PageHeader")]'
            '//h1[contains(@class, "page-header__title")]'
            '/text()'
        ).extract_first()

        if artist_name:
            artist_name=artist_name.strip()
            # Get all songs
            songs = response.xpath(
                '//div[contains(@id, "WikiaArticle")]'
                '//div[contains(@id, "mw-content-text")]'
                '/ol'
                '/li'
                '/b'
                '/a[not(contains(@class, "new"))]'
            )

            for song in songs:
                song_title = song.xpath('./text()').extract_first().strip()
                song_url = song.xpath('./@href').extract_first()

                req_meta = {
                    "title": song_title,
                    "artist": artist_name
                }

                yield response.follow(
                    song_url,
                    callback=self._song,
                    meta=req_meta,
                    priority=1000
                )

    def _artist_listing(self, response):
        self.logger.debug("Current listing page: {}".format(response.url))

        # Get links to artist pages
        artist_pages = response.xpath(
            '//div[contains(@id, "WikiaArticle")]'
            '//div[contains(@id, "mw-pages")]'
            '//div[contains(@class, "mw-content-ltr")]'
            '//a'
            '/@href'
        ).extract()

        for artist_url in artist_pages:
            yield response.follow(
                artist_url,
                callback=self._artist,
                priority=100
            )

    def _artist_category_main(self, response):
        self.logger.debug("Current artist category page: {}".format(
            response.url))

        # Get subcategories
        subcategories = response.xpath(
            '//div[contains(@id, "WikiaArticle")]'
            '//div[contains(@id, "mw-subcategories")]'
            '//a[contains(@class, "CategoryTreeLabelCategory")]'
            '/@href'
        ).extract()

        for link in subcategories:
            yield response.follow(
                link,
                callback=self._artist_category_main,
                priority=-1
            )

        # Get pagination
        max_pagination = max([int(x) for x in response.xpath(
            '//div[contains(@id, "WikiaArticle")]'
            '//div[contains(@class, "wikia-paginator")]'
            '//a[contains(@class, "paginator-page")]'
            '/@data-page'
        ).extract()] + [1])

        for i in range(1, max_pagination + 1):
            yield response.follow(
                response.url + "?page=%s" % i,
                callback=self._artist_listing,
                priority=10
            )

    def parse(self, response):
        artist_categories_pages = response.xpath(
            '//div[contains(@id, "WikiaArticle")]'
            '//div[contains(@id, "mw-subcategories")]'
            '//a[contains(@class, "CategoryTreeLabelCategory")]'
            '/@href'
        ).extract()

        for link in artist_categories_pages:
            yield response.follow(
                link,
                callback=self._artist_category_main,
                priority=-1
            )
