# coding=utf-8

import scrapy
import logging
import re

from proxy import Proxy
from .basespider import BaseSpider


class CN66ipSpider(BaseSpider):
    name = '66ip'

    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    base_url = 'http://www.66ip.cn'

    def __init__(self, *a, **kwargs):
        super(CN66ipSpider, self).__init__(*a, **kwargs)

        self.urls = ['http://www.66ip.cn/areaindex_%s/1.html' % n for n in range(1, 34)]

        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        trs = response.css('#footer table tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 5:
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
            next_url = None
            last = response.css('#PageList a')[-1]
            if last.xpath('@class').extract_first() != 'pageCurrent':
                next_url = last.xpath('@href').extract_first()
                next_url = self.base_url + next_url
            return next_url
        except Exception as e:
            print e
            return None
