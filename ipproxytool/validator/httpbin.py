# -*- coding: utf-8 -*-

import json
import time
import requests
import config
import logging
import datetime

from scrapy import Request
from .validator import Validator


class HttpBinSpider(Validator):
    name = 'httpbin'
    concurrent_requests = 16

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'CONCURRENT_REQUESTS': 4000,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2000,
    }

    def __init__(self, name=None, **kwargs):
        super(HttpBinSpider, self).__init__(name, **kwargs)
        self.timeout = 20
        self.urls = [
            'http://httpbin.org/get?show_env=1',
            'https://httpbin.org/get?show_env=1',
        ]
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Host": "httpbin.org",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0"
        }

        self.origin_ip = ''

        self.query = {
            'httpbin': {'$ne': False}
        }

        # self.init()

    def init(self):
        super(HttpBinSpider, self).init()

        r = requests.get(url=self.urls[0], timeout=20)
        data = json.loads(r.text)
        self.origin_ip = data.get('origin', '')
        logging.info('origin ip:%s' % self.origin_ip)

    def valid(self, cur_time, proxy_info, proxy):
        proxies = {
            'http': proxy,
            'https': proxy,
        }
        start_time = time.time()
        r = requests.get(url=self.urls[0], proxies=proxies, timeout=20)
        end_time = time.time()
        speed = end_time - start_time
        logging.info('%s :%d' % (proxy, r.status_code))
        if r.status_code == 200:
            proxy_info['speed'] = time.time() - cur_time
            proxy_info['vali_count'] += 1
            data = json.loads(r.text)
            origin = data.get('origin')
            headers = data.get('headers')
            x_forwarded_for = headers.get('X-Forwarded-For', None)
            x_real_ip = headers.get('X-Real-Ip', None)
            via = headers.get('Via', None)

            if self.origin_ip in origin:
                proxy_info['anonymity'] = 3
            elif via is not None:
                proxy_info['anonymity'] = 2
            elif x_forwarded_for is not None and x_real_ip is not None:
                proxy_info['anonymity'] = 1

            query = {
                'ip': proxy_info['ip']
            }
            update_set = {
                '$set': {
                    'httpbin_speed': speed,
                    'httpbin_vali_count': proxy_info['vali_count'],
                    'httpbin_err_count': 0,
                    'httpbin_vali_time': str(datetime.datetime.now()),
                    'httpbin': True
                }
            }
            self.sql.db[config.free_ipproxy_table].update(query, update_set)
            # self.sql.insert_proxy(
            #     table_name=self.name, proxy=proxy_info)
        else:
            # 如果验证次数超过最大次数，就标记False
            query = {
                'ip': proxy_info['ip']
            }
            httpbin_err_count = proxy_info.get('httpbin_err_count', 0)
            if httpbin_err_count >= config.max_err_count:
                update_set = {
                    '$set': {
                        'httpbin': False
                    }
                }
            else:
                update_set = {
                    '$set': {
                        'httpbin_err_count': httpbin_err_count + 1,
                        'httpbin_vali_time': str(datetime.datetime.now()),
                    }
                }
            self.sql.db[config.free_ipproxy_table].update(query, update_set)
        return False
