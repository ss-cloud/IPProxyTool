# -*- coding: utf-8 -*-

import os
import logging
import sys

from ipproxytool.validator.douban import DoubanSpider
from ipproxytool.validator.assetstore import AssetStoreSpider
from ipproxytool.validator.gather import GatherSpider
from ipproxytool.validator.httpbin import HttpBinSpider
from ipproxytool.validator.steam import SteamSpider
from ipproxytool.validator.boss import BossSpider
from ipproxytool.validator.lagou import LagouSpider
from ipproxytool.validator.liepin import LiepinSpider
from ipproxytool.validator.jd import JDSpider
from ipproxytool.validator.bbs import BBSSpider
from ipproxytool.validator.zhilian import ZhiLianSpider
from ipproxytool.validator.amazoncn import AmazonCnSpider


l = locals()


def runspider(name):
    # init logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log/%s.log' % name,
                        filemode='w')

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

    V = l.get(name)
    v = V()
    v.start_requests()

    logging.debug('finish this spider:%s\n\n' % name)


if __name__ == '__main__':
    # try:
    name = sys.argv[1] or 'base'
    runspider(name)
    # except Exception as e:
    #     logging.exception('run_spider main exception msg:%s' % e)
