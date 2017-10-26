# -*- coding: utf-8 -*-
import os
import re
from copy import copy

import scrapy

from lyrics_crawler.items import LyricsCrawlerItem


class MetroLyricsSpider(scrapy.Spider):
    name = 'MetroLyrics.com'
    allowed_domains = ['metrolyrics.com']

    start_urls = [
        f"http://www.metrolyrics.com/artists-{letter}.html"
        for letter in os.environ.get("PAGES", "1abcdefghijklmnopqrstuvwxyz")
    ]

    def _err_handler(self, failure):
        self.logger.error("Failure: " + repr(failure))
        self.logger.error("-> " + failure.response.url)

    def _artist_page_parse(self, response):
        self.logger.info(
            "[{} QUEUE] [ARTIST] {}".format(
                len(self.crawler.engine.slot.scheduler),
                response.meta['artist']['artist']
            ))

        # Get by-album page url
        album_list = response.xpath(
            '//a[contains(@data-ref, "albums")]/@href').extract_first()

        yield response.follow(
            album_list,
            callback=self._album_list_parse,
            errback=self._err_handler,
            meta=response.meta,
            priority=100
        )

    def _album_list_parse(self, response):
        meta = response.meta['artist']

        albums = response.xpath('//div[contains(@class, "album-track-list")]')
        for album in albums:
            album_meta = copy(meta)
            album_meta['album'] = album.xpath(
                './/header//h3/span//text()').extract_first()

            year = album.xpath(".//header//h3/text()").extract_first() or ""
            year = year.strip(" ()")

            if year:
                album_meta['year'] = int(year)

            song_urls = album.xpath('.//div[contains(@class, "song-list")]' +
                                    '//li//a')

            for song in song_urls:
                album_meta['title'] = song.xpath(
                    './text()').extract_first().replace(
                    'Lyrics', '').strip()
                song_url = song.xpath("./@href").extract_first()

                req_meta = {"album": copy(album_meta)}
                yield response.follow(
                    song_url,
                    callback=self._song_parse,
                    errback=self._err_handler,
                    meta=req_meta,
                    priority=1000000
                )

        # Follow next page
        next_page = response.xpath(
            '//p[contains(@class, "pagination")]/a[contains(@class, "next")]'
            '/@href'
        ).extract_first()

        if next_page and next_page.startswith("http"):
            yield response.follow(
                next_page,
                callback=self._album_list_parse,
                errback=self._err_handler,
                meta=response.meta,
                priority=1000
            )

    def _song_parse(self, response):
        self.logger.info("[{} QUEUE] [SONG] {}: {}".format(
            len(self.crawler.engine.slot.scheduler),
            response.meta['album']['artist'], response.meta['album']['title']))

        song_meta = response.meta['album']

        song_meta['song_id'] = response.url.replace(
            "http://www.metrolyrics.com/", "").replace(
            "-lyrics", "").replace(
            ".html", ""
        )

        verses = response.xpath('//div[contains(@id, "lyrics-body-text")]' +
                                '//p[contains(@class, "verse")]' +
                                '//text()').extract()

        song_meta['lyrics'] = verses

        yield LyricsCrawlerItem(song_meta)

    def _artist_list_parse(self, response):
        self.logger.info("Current pagination page: {}".format(response.url))

        for artist in response.xpath(
                '//table[contains(@class, "songs-table")]/tbody//tr'):
            artist_url = artist.xpath(
                './meta[contains(@itemprop, "url")]/@content'
            ).extract_first()

            meta = {
                "artist":
                    artist.xpath(
                        './meta[contains(@itemprop, "name")]/@content'
                    ).extract_first(),
                "artist_id":
                    artist_url.replace(
                        "http://www.metrolyrics.com/", "").replace(
                        "-lyrics.html", ""),
                "artist_popularity":
                    float(
                        re.findall(
                            r"width:(\d+\.?\d{,2})",
                            artist.xpath(
                                './/span[contains(@class, "bar")]/span/@style'
                            ).extract_first()
                        )[0]
                    )
            }
            req_meta = {"artist": copy(meta)}
            yield response.follow(
                artist_url,
                callback=self._artist_page_parse,
                errback=self._err_handler,
                meta=req_meta,
                priority=-20
            )

        # Follow next page
        next_page = response.xpath(
            '//p[contains(@class, "pagination")]/a[contains(@class, "next")]'
            '/@href'
        ).extract_first()

        if next_page and next_page.startswith("http"):
            self.logger.info("Next page: '{}'".format(
                next_page
            ))
            yield response.follow(
                next_page,
                callback=self._artist_list_parse,
                errback=self._err_handler,
                priority=-80
            )
        else:
            self.logger.warning("No further pagination after '{}'".format(
                response.url
            ))

    def parse(self, response):
        # Get first pagination url
        initial_page = response.xpath(
            '//p[contains(@class, "pagination")]/a[contains(@class, "next")]'
            '/@href'
        ).extract_first()

        if initial_page and initial_page.startswith("http"):
            yield response.follow(
                initial_page,
                callback=self._artist_list_parse,
                errback=self._err_handler,
                priority=-1000
            )
