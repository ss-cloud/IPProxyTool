#-*- coding: utf-8 -*-

import re
import scrapy
import logging
import base64

from proxy import Proxy
from .basespider import BaseSpider


class CoolProxySpider(BaseSpider):
    name = 'nianshao'

    base_url = "http://www.nianshao.me"

    # custom_settings = {
    #     'LOG_LEVEL': 'DEBUG',
    # }

    def __init__(self, *a, **kwargs):
        super(CoolProxySpider, self).__init__(*a, **kwargs)

        self.urls = [
            'http://www.nianshao.me/?stype=1&page=1',
            'http://www.nianshao.me/?stype=2&page=1',
            'http://www.nianshao.me/?stype=3&page=1',
            'http://www.nianshao.me/?stype=4&page=1',
            'http://www.nianshao.me/?stype=5&page=1',
        ]

        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        trs = response.css('#main table tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 8:
                continue

            ip = tds[0].xpath('text()').extract_first()
            port = tds[1].xpath('text()').extract_first()
            country = tds[2].xpath('text()').extract_first()
            anonymity = tds[3].xpath('text()').extract_first()

            proxy = Proxy()
            proxy.set_value(
                ip=ip,
                port=port,
                country=country,
                anonymity=anonymity,
                source=self.name,
            )

            self.add_proxy(proxy)

    def parse_next_url(self, response):
        try:
            now_page = response.css('#listnav a[class="active"]::text').extract_first()
            now_page = int(now_page)
            last_page = response.css('#listnav a::text').extract()[-1]
            last_page = int(last_page)
            next_page = now_page + 1

            if last_page >= next_page:
                url = str(response.url)
                next_url = url.replace("page=" + str(now_page), "page=" + str(next_page))
                return next_url
        except Exception as e:
            print e
            return None
