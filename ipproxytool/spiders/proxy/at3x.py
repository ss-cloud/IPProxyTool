#-*- coding: utf-8 -*-

import re
import scrapy
import logging

from proxy import Proxy
from .basespider import BaseSpider


class AT3XSpider(BaseSpider):
    name = 'at3x'

    base_url = "http://at3x.com"

    def __init__(self, *a, **kwargs):
        super(AT3XSpider, self).__init__(*a, **kwargs)

        self.urls = [
            'http://at3x.com/?page=1',
        ]

        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        trs = response.css('.table-striped tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 7:
                continue

            ip = tds[1].xpath('a/text()').extract_first()
            port = tds[2].xpath('text()').extract_first()
            anonymity = tds[3].xpath('a/text()').extract_first()

            proxy = Proxy()
            proxy.set_value(
                ip=ip,
                port=port,
                country='None',
                anonymity=anonymity,
                source=self.name,
            )

            self.add_proxy(proxy)

    def parse_next_url(self, response):
        next_url = response.css(u'a[aria-label="Next"]::attr(href)').extract_first()
        if next_url:
            return self.base_url + next_url
        return None
