# -*- coding: utf-8 -*-

import logging
import os
import sys
import scrapydo
import time
import utils
import config
import multiprocessing

from sql import SqlManager

from ipproxytool.spiders.proxy.at3x import AT3XSpider
from ipproxytool.spiders.proxy.cn31f import CN31FSpider
from ipproxytool.spiders.proxy.coolproxy import CoolProxySpider
from ipproxytool.spiders.proxy.data5u import Data5uSpider
from ipproxytool.spiders.proxy.freeproxylists import FreeProxyListsSpider
from ipproxytool.spiders.proxy.ip181 import IpOneEightOneSpider
from ipproxytool.spiders.proxy.ip3366 import IP3366Spider
from ipproxytool.spiders.proxy.kuaidaili import KuaiDaiLiSpider
from ipproxytool.spiders.proxy.nianshao import CoolProxySpider
from ipproxytool.spiders.proxy.proxydb import ProxyDBSpider
from ipproxytool.spiders.proxy.xicidaili import XiCiDaiLiSpider


scrapydo.setup()


def run_crawl(spider):
    #######################################################################
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    console.setFormatter(formatter)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.ERROR)
    logging.getLogger('').addHandler(console)

    scrapydo.run_spider(spider_cls=spider)

if __name__ == '__main__':
    os.chdir(sys.path[0])

    if not os.path.exists('log'):
        os.makedirs('log')

    # init logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log/crawl_proxy.log',
                        filemode='w')

    spiders = [
        AT3XSpider,
        CN31FSpider,
        CoolProxySpider,
        Data5uSpider,
        FreeProxyListsSpider,
        IpOneEightOneSpider,
        IP3366Spider,
        KuaiDaiLiSpider,
        CoolProxySpider,
        ProxyDBSpider,
        XiCiDaiLiSpider,
    ]

    num_spider = len(spiders)
    pool = multiprocessing.Pool(processes=num_spider)

    for spider in spiders:
        print spider
        pool.apply_async(run_crawl, (spider,))

    pool.close()
    pool.join()
    print "Sub-process(es) done."
