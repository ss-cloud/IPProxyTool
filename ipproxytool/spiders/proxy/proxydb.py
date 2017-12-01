# coding=utf-8
import scrapy
import logging

from proxy import Proxy
from .basespider import BaseSpider
from scrapy.selector import Selector


class ProxyDBSpider(BaseSpider):
    name = 'proxydb'

    base_url = 'http://proxydb.net'

    custom_settings = {
        'LOG_LEVEL': 'DEBUG',
    }

    def __init__(self, *a, **kwargs):
        super(ProxyDBSpider, self).__init__(*a, **kwargs)

        self.urls = ['http://proxydb.net/']

        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        trs = response.css('.table-striped tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 8:
                continue

            ipport = tds[1].xpath('text()').extract_first()
            port = tds[2].xpath('text()').extract_first()
            country = tds[3].xpath('a/text()').extract_first()
            anonymity = tds[4].xpath('a/text()').extract_first()

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
        next_el = response.css(u'a.pagination-next')
        if next_el.xpath('@disabled').extract_first() != 'disabled':
            next_url = next_el.xpath('@href').extract_first()
            print next_url
            return self.base_url + next_url
        return None
