# -*- coding: utf-8 -*-
import logging
import random
import time
import datetime
import utils
import config
import SimplePool
import threading

from proxy import Proxy
from sql import SqlManager


class ValidThread(threading.Thread):

    def __init__(self, threadpool):
        self.threadpool = threadpool
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(1)
            logging.error('unfinished_tasks : %d' % self.threadpool.unfinished_tasks())


class Validator(object):
    name = 'base'
    concurrent_requests = 16
    retry_enabled = False

    def __init__(self, name=None, **kwargs):

        self.urls = []
        self.headers = None
        self.timeout = 10
        self.success_status = [200]
        self.is_record_web_page = False

        self.sql = SqlManager()

        self.threadpool = SimplePool.ThreadPool(config.thread_num)

    def init(self):
        self.dir_log = 'log/validator/%s' % self.name
        utils.make_dir(self.dir_log)

        self.sql.init_proxy_table(self.name)

    def start_requests(self):
        count = self.sql.get_proxy_count(config.free_ipproxy_table)
        count_free = self.sql.get_proxy_count(config.httpbin_table)

        # ids = self.sql.get_proxy_ids(config.free_ipproxy_table)
        # ids_httpbin = self.sql.get_proxy_ids(config.httpbin_table)

        for data in self.sql.select_proxy(config.free_ipproxy_table):
            url = random.choice(self.urls)
            cur_time = time.time()

            proxy = Proxy()
            proxy.set_value(
                ip=data.get('ip'),
                port=data.get('port'),
                country=data.get('country'),
                anonymity=data.get('country'),
                https=data.get('https'),
                speed=data.get('speed'),
                source=data.get('source'),
                vali_count=data.get('vali_count')
            )
            proxy.id = data.get('_id')

            args = (
                cur_time,
                proxy,
                'http://%s:%s' % (proxy.ip, proxy.port)
            )

            j = SimplePool.ThreadJob(self.valid, args)

            self.threadpool.add_job(j)

        result = ValidThread(self.threadpool)
        result.start()
        self.threadpool.start()
        self.threadpool.finish()

    def valid(self, cur_time, proxy_info, proxy):
        print proxy

    def success_parse(self, response):
        proxy = response.meta.get('proxy_info')
        table = response.meta.get('table')

        self.save_page(proxy.ip, response.body)
        self.log('success_parse speed:%s meta:%s' %
                 (time.time() - response.meta.get('cur_time'), response.meta))

        proxy.vali_count += 1
        proxy.speed = time.time() - response.meta.get('cur_time')
        if self.success_content_parse(response):
            if table == self.name:
                if proxy.speed > self.timeout:
                    self.sql.del_proxy_with_id(table, proxy.id)
                else:
                    self.sql.update_proxy(table, proxy)
            else:
                if proxy.speed < self.timeout:
                    self.sql.insert_proxy(table_name=self.name, proxy=proxy)
        else:
            if table == self.name:
                self.sql.del_proxy_with_id(table_name=table, id=proxy.id)

        self.sql.commit()

    def success_content_parse(self, response):
        if response.status not in self.success_status:
            return False
        return True

    def error_parse(self, failure):
        request = failure.request
        self.log('error_parse value:%s url:%s meta:%s' %
                 (failure.value, request.url, request.meta))

        proxy = failure.request.meta.get('proxy_info')
        table = failure.request.meta.get('table')

        if table == self.name:
            self.sql.del_proxy_with_id(table_name=table, id=proxy.id)
        else:
            # TODO... 如果 ip 验证失败应该针对特定的错误类型，进行处理
            pass

            #
            # request = failure.request.meta
            # utils.log('request meta:%s' % str(request))
            #
            # # log all errback failures,
            # # in case you want to do something special for some errors,
            # # you may need the failure's type
            # self.logger.error(repr(failure))
            #
            # #if isinstance(failure.value, HttpError):
            # if failure.check(HttpError):
            #     # you can get the response
            #     response = failure.value.response
            #     self.logger.error('HttpError on %s', response.url)
            #
            # #elif isinstance(failure.value, DNSLookupError):
            # elif failure.check(DNSLookupError):
            #     # this is the original request
            #     request = failure.request
            #     self.logger.error('DNSLookupError on %s', request.url)
            #
            # #elif isinstance(failure.value, TimeoutError):
            # elif failure.check(TimeoutError):
            #     request = failure.request
            #     self.logger.error('TimeoutError on url:%s', request.url)

    def save_page(self, ip, data):
        filename = '{time} {ip}'.format(time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f'), ip=ip)

        if self.is_record_web_page:
            with open('%s/%s.html' % (self.dir_log, filename), 'wb') as f:
                f.write(data)
                f.close()

    def close(spider, reason):
        spider.sql.commit()
