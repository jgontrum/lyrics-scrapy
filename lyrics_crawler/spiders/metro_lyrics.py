# -*- coding: utf-8 -*-
from copy import copy

import scrapy
import re

from lyrics_crawler.items import LyricsCrawlerItem


class ExampleSpider(scrapy.Spider):
    name = 'MetroLyrics.com'
    allowed_domains = ['metrolyrics.com']

    start_urls = [
        f"http://www.metrolyrics.com/artists-{letter}.html"
        for letter in "1"  # "1abcdefghijklmnopqrstuvwxyz"
    ]

    def _get_next_page(self, response):
        next_url = response.xpath(
            '//p[contains(@class, "pagination")]/a[contains(@class, "next")]/@href'
        ).extract_first()

        if next_url and next_url.startswith("http"):
            return next_url

    def _artist_page_parse(self, response):
        meta = response.meta['artist']
        self.logger.info("Artist: {}".format(meta['artist']))

        # Get by-album page url
        album_list = response.xpath(
            '//a[contains(@data-ref, "albums")]/@href').extract_first()

        request = response.follow(album_list, self._album_list_parse)
        request.meta['artist'] = meta
        yield request

    def _album_list_parse(self, response):
        artist_meta = response.meta['artist']

        albums = response.xpath('//div[contains(@class, "album-track-list")]')
        for album in albums:
            album_meta = copy(artist_meta)
            album_meta['album'] = album.xpath(
                './/header//h3/span//text()').extract_first()

            year = album.xpath(".//header//h3/text()").extract_first() or ""
            year = year.strip((" ()"))

            if year:
                album_meta['year'] = int(year)

            song_urls = album.xpath('.//div[contains(@class, "song-list")]' +
                                    '//li//a')

            for song in song_urls:
                title = song.xpath('./text()').extract_first().replace(
                    'Lyrics', '').strip()
                song_url = song.xpath("./@href").extract_first()

                request = response.follow(song_url, self._song_parse)
                request.meta['album'] = album_meta
                request.meta['song'] = title
                yield request

        return  # TODO remove
        # Follow next page
        next_page = self._get_next_page(response)
        if next_page:
            request = response.follow(next_page, self._album_list_parse)
            request.meta['artist'] = artist_meta
            yield request

    def _song_parse(self, response):
        self.logger.info("Song: {}".format(response.meta['song']))

        song_meta = copy(response.meta['album'])
        song_meta['title'] = response.meta['song']

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

            request = response.follow(artist_url, self._artist_page_parse)
            request.meta['artist'] = meta
            yield request
            return  # TODO REMOVE

        return  # TODO REMOVE
        # Follow next page
        next_page = self._get_next_page(response)
        if next_page:
            yield response.follow(next_page, self._artist_list_parse)

    def parse(self, response):
        # Get first pagination url
        initial_page = self._get_next_page(response)

        if initial_page:
            yield response.follow(initial_page, self._artist_list_parse)
