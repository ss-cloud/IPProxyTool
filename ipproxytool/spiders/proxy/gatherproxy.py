# coding=utf-8

import json
import random
import re
import scrapy
import requests
import logging

from proxy import Proxy
from .basespider import BaseSpider


class GatherproxySpider(BaseSpider):
    name = 'gatherproxy'

    base_url = 'http://www.gatherproxy.com'

    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *a, **kwargs):
        super(GatherproxySpider, self).__init__(*a, **kwargs)

        self.areas = ['China', 'Brazil', 'United States', 'Indonesia', 'Russia', 'Thailand', 'United Kingdom', 'India', 'Bangladesh',
                      'Venezuela', 'Ukraine', 'France', 'Iran', 'Germany', 'Colombia', 'Argentina', 'Poland', 'Canada', 'Czech Republic',
                      'Singapore', 'Mexico', 'Australia', 'Turkey', 'Vietnam', 'Taiwan', 'Italy', 'Hong Kong', 'Netherlands', 'South Africa',
                      'Spain', 'Ecuador', 'Republic of Korea', 'Philippines', 'Pakistan', 'Japan', 'Bulgaria', 'Nigeria', 'Chile', 'Peru',
                      'Egypt', 'Cambodia', 'Romania', 'Hungary', 'Malaysia', 'Iraq', 'Denmark', 'Republic of Moldova', 'Albania', 'Czechia',
                      'Nepal', 'Kenya', 'Bolivia', 'Serbia', 'Kazakhstan', 'Republic of Lithuania', 'Austria', 'Greece', 'Georgia', 'Paraguay',
                      'Ireland', 'Israel', 'Mongolia', 'Bosnia and Herzegovina', 'Palestine', 'Slovak Republic', 'Belarus', 'Sweden', 'Azerbaijan',
                      'Afghanistan', 'Cameroon', 'Tanzania', 'Honduras', 'Unknown', 'Yemen', 'Zimbabwe', 'Saudi Arabia', 'Guatemala', 'Gabon',
                      'Dominican Republic', 'Mozambique', 'Puerto Rico', 'El Salvador', 'Costa Rica', 'Portugal', 'Myanmar [Burma]'
                      ',Ivory Coast', 'Panama', 'Algeria', 'Kyrgyzstan', 'Seychelles', 'Libya', 'Mauritius', 'Sri Lanka', 'Belgium',
                      'Switzerland', 'Croatia', 'Zambia', 'Madagascar', 'New Zealand', 'New Caledonia', 'Malawi', 'Rwanda', 'Uruguay',
                      'Syria', 'Lebanon', 'Macedonia', 'Armenia', 'Jamaica', 'Norway', 'Laos', 'Macao', 'Malta', 'Ghana', 'Djibouti',
                      'Lesotho', 'Botswana', 'East Timor', 'Guinea', 'Uganda', 'Latvia', 'Somalia', 'Sierra Leone', 'Equatorial Guinea',
                      'Maldives', 'Benin', 'Mali', 'Luxembourg', 'Slovenia', 'Uzbekistan', 'Morocco', 'United Arab Emirates']

        self.anonymities = ['Transparent', 'Elite', 'Anonymous']

        self.proxy = "http://localhost:1080"
        self.init()
        self.method = 'POST'
        self.formdata = {
            'Type': 'transparent',
            'PageIdx': '1',
            'Uptime': '0'
        }

    def start_requests(self):
        for area in self.areas:
            url = '%s/proxylist/country/?c=%s&PageIdx' % (self.base_url, area)
            self.formdata = {
                'Country': area.lower(),
                'PageIdx': '1'
            }
            yield scrapy.FormRequest(
                url=url,
                formdata=self.formdata,
                meta=self.meta,
                dont_filter=True,
                callback=self.parse_page,
                errback=self.error_parse,
            )
        for anonymitiy in self.anonymities:
            url = '%s/proxylist/anonymity/?t=%s&PageIdx' % (self.base_url, anonymitiy)
            self.formdata = {
                'Type': anonymitiy.lower(),
                'PageIdx': '1'
            }
            yield scrapy.FormRequest(
                url=url,
                formdata=self.formdata,
                meta=self.meta,
                dont_filter=True,
                callback=self.parse_page,
                errback=self.error_parse,
            )

    def parse_page(self, response):
        logging.info("parse_page :%s" % response.url)
        next_url = self.parse_next_url(response)
        if next_url:
            yield scrapy.FormRequest(
                url=next_url,
                formdata=self.formdata,
                meta=self.meta,
                dont_filter=True,
                callback=self.parse_page,
                errback=self.error_parse,
            )

        trs = response.css('#tblproxy tr')
        for tr in trs:
            tds = tr.css("td")
            if len(tds) != 8:
                continue

            ip = tds[1].xpath('script/text()').extract_first()
            port = tds[2].xpath('script/text()').extract_first()
            country = tds[4].xpath('text()').extract_first()
            anonymity = tds[3].xpath('text()').extract_first()

            try:
                ip = re.search(r"write\(\'(\S+)\'", ip).group(1)
            except Exception as e:
                continue

            try:
                port = re.search(r"dep\(\'(\S+)\'", port).group(1)
                port = int(port, 16)
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
        try:
            next_url = None
            now_page = int(self.formdata.get('PageIdx', '1'))
            last = response.css('.pagenavi a')[-1]
            last_page = int(last.xpath('text()').extract_first())
            if last_page > now_page:
                next_url = response.url
                self.formdata['PageIdx'] = str(now_page + 1)
            return next_url
        except Exception as e:
            print e
            return None
