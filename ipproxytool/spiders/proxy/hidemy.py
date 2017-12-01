# #-*- coding: utf-8 -*-

# import urllib
# import re
# import scrapy
# import logging

# from .basespider import BaseSpider
# from proxy import Proxy


# class HidemySpider(BaseSpider):
#     name = 'hidemy'

#     base_url = 'https://hidemy.name'

#     custom_settings = {
#         'LOG_LEVEL': 'DEBUG',
#     }

#     def __init__(self, *a, **kw):
#         super(HidemySpider, self).__init__(*a, **kw)

#         self.urls = ['https://hidemy.name/en/proxy-list/']

#         self.proxy = "http://localhost:1080"
#         self.init()

#     def parse_page(self, response):
#         logging.info("parse_page :%s" % response.url)
#         next_url = self.parse_next_url(response)
#         if next_url:
#             yield scrapy.Request(url=next_url, callback=self.parse_page)

#         trs = response.css('.proxy__t tbody tr')
#         for tr in trs:
#             tds = tr.css("td")
#             if len(tds) != 7:
#                 continue

#             ip = tds[0].xpath('script/text()').extract_first()
#             port = tds[1].xpath('text()').extract_first()
#             country = tds[2].xpath('div/span/text()').extract_first()
#             anonymity = tds[5].xpath('text()').extract_first()

#             proxy = Proxy()
#             proxy.set_value(
#                 ip=ip,
#                 port=port,
#                 country=country,
#                 anonymity=anonymity,
#                 source=self.name,
#             )
#             logging.info(proxy.get_dict())
#             break

#             self.add_proxy(proxy)

#     def parse_next_url(self, response):
#         next_url = response.css(u'.arrow__right a::attr(href)').extract_first()
#         if next_url:
#             return self.base_url + next_url
#         return None
