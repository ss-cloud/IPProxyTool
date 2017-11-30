#-*- coding: utf-8 -*-
import re
import scrapy
import logging

from scrapy import Selector
from .basespider import BaseSpider
from proxy import Proxy


class IP3366Spider(BaseSpider):
    name = 'ip3366'

    base_url = "http://www.ip3366.net"

    def __init__(self, *a, **kw):
        super(IP3366Spider, self).__init__(*a, **kw)

        self.urls = [
            'http://www.ip3366.net/free/?stype=1&page=1',
            'http://www.ip3366.net/free/?stype=2&page=1',
            'http://www.ip3366.net/free/?stype=3&page=1',
            'http://www.ip3366.net/free/?stype=4&page=1',
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

            ip = tds[0].xpath('text()').extract_first()
            port = tds[1].xpath('text()').extract_first()
            anonymity = tds[2].xpath('text()').extract_first()
            country = tds[4].xpath('text()').extract_first()

            proxy = Proxy()
            proxy.set_value(
                ip=ip,
                port=port,
                country=country,
                anonymity=anonymity,
                source=self.name,
            )
            print proxy.get_dict()
            break

            self.add_proxy(proxy)

    def parse_next_url(self, response):
        try:
            now_page = re.search(r'page=([\d+])', response.url).group(1)
            now_page = int(now_page)
            last_page = response.css('#listnav strong::text').extract_first().replace('/', '')
            print last_page
            last_page = int(last_page)
            next_page = now_page + 1

            print now_page, last_page
            if last_page >= next_page:
                url = str(response.url)
                next_url = url.replace("page=" + str(now_page), "page=" + str(next_page))
                return next_url
        except Exception as e:
            print e
            return None
