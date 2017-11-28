#-*- coding: utf-8 -*-

import re
import scrapy
import logging

from proxy import Proxy
from .basespider import BaseSpider


class KuaiDaiLiSpider(BaseSpider):
    name = 'kuaidaili'

    base_url = "http://www.kuaidaili.com/"

    def __init__(self, *a, **kwargs):
        super(KuaiDaiLiSpider, self).__init__(*a, **kwargs)

        self.urls = [
            'http://www.kuaidaili.com/free/inha/1',
            'http://www.kuaidaili.com/free/intr/1',
        ]

        self.headers = {
            'Host': 'www.kuaidaili.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0',
            # 'Referer': 'http://www.kuaidaili.com/free/inha/1/',
        }

        self.is_record_web_page = False
        self.init()

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.Request(url=next_url, callback=self.parse_page)

        pattern = re.compile(
            '<tr>\s.*?<td.*?>(.*?)</td>\s.*?<td.*?>(.*?)</td>\s.*?<td.*?>(.*?)</td>\s.*?<td.*?>('
            '.*?)</td>\s.*?<td.*?>(.*?)</td>\s.*?<td.*?>(.*?)</td>\s.*?<td.*?>(.*?)</td>\s.*?</tr>',
            re.S)
        items = re.findall(pattern, response.body)

        for item in items:
            proxy = Proxy()
            proxy.set_value(
                ip=item[0],
                port=item[1],
                country=item[4],
                anonymity=item[2],
                source=self.name,
            )

            self.add_proxy(proxy)

    def parse_next_url(self, response):
        try:
            now_page = response.css('a[class="active"]::text').extract_first()
            now_page = int(now_page)
            last_page = response.css('#listnav li a::text').extract()[-1]
            last_page = int(last_page)
            next_page = now_page + 1

            if last_page >= next_page:
                url = str(response.url)
                next_url = url.replace(str(now_page), str(next_page))
                return next_url
        except Exception as e:
            print e
            return None
