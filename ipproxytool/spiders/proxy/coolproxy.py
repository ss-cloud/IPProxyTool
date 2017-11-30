#-*- coding: utf-8 -*-

import re
import scrapy
import logging
import base64

from proxy import Proxy
from .basespider import BaseSpider


class CoolProxySpider(BaseSpider):
    name = 'coolproxy'

    base_url = "https://www.cool-proxy.net"

    # custom_settings = {
    #     'LOG_LEVEL': 'DEBUG',
    # }

    def __init__(self, *a, **kwargs):
        super(CoolProxySpider, self).__init__(*a, **kwargs)

        self.urls = [
            'https://www.cool-proxy.net/proxies/http_proxy_list/sort:score/direction:desc',
        ]

        self.proxy = "http://localhost:1080"
        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        trs = response.css('#main table tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 10:
                continue

            ip = tds[0].xpath('script/text()').extract_first()
            port = tds[1].xpath('text()').extract_first()
            country = tds[3].xpath('text()').extract_first()
            anonymity = tds[5].xpath('text()').extract_first()

            try:
                ip = re.search(r"str_rot13\(\"(\S+)\"", ip).group(1)
                ip = self.decode_ip(ip)
            except Exception as e:
                continue

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
        next_url = response.css(u'a[rel="next"]::attr(href)').extract_first()
        if next_url:
            return self.base_url + next_url
        return None

    def decode_ip(self, strs):
        real_ip = ""
        for s in strs:
            if re.match(r'[a-z]', s, re.IGNORECASE):
                o = ord(s) + (13 if s.lower() < 'n' else -13)
                s = chr(o)
            real_ip = real_ip + s
        return base64.b64decode(real_ip)
