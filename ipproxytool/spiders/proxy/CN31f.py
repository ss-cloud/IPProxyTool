#-*- coding: utf-8 -*-

import re
import scrapy
import logging

from proxy import Proxy
from .basespider import BaseSpider


class CN31FSpider(BaseSpider):
    name = '31f'

    base_url = "http://31f.cn"

    def __init__(self, *a, **kwargs):
        super(CN31FSpider, self).__init__(*a, **kwargs)

        areas = ['美国',   '巴西',   '印度尼西亚',    '俄罗斯',  '泰国',   '北美地区',
                 '加拿大',  '瑞典',   '台湾省',  '亚太地区', '德国',   '拉美地区',
                 '马来西亚', '印度',   '英国',   '香港',   '乌克兰',  'IANA',
                 '罗马尼亚', '法国',   '台湾省台北市',   '挪威',   '委内瑞拉', '意大利',
                 '欧洲和中东地区',  '伊朗',   '土耳其',  '波兰',   '墨西哥',  '澳大利亚',
                 '新加坡',  '厄瓜多尔', '荷兰',   '孟加拉',  '日本',   '保加利亚',
                 '哥伦比亚', '北京市',  '韩国',   '阿根廷',  '捷克',   '越南',
                 '菲律宾',  '西班牙',  '柬埔寨',  '巴基斯坦', '欧洲',   '秘鲁',
                 '智利',   '南非',   '丹麦',   '安徽省淮南市',   '埃及',   '芬兰',
                 '非洲',   '浙江省杭州市',   '新西兰',  '中国',   '肯尼亚',  '瑞士']
        for area in areas:
            url = '%s/area/%s/' % (self.base_url, area)
            self.urls.append(url)
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

            ip = tds[1].xpath('text()').extract_first()
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
        next_url = response.css(u'a[aria-label="Next"]::attr(href)').extract_first()
        if next_url:
            return self.base_url + next_url
        return None
