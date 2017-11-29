# -*- coding: utf-8 -*-

import logging
import os
import subprocess
import sys
import time
import scrapydo
import utils

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

scrapydo.setup()


def validator():
    validators = [
        HttpBinSpider,  # 必须
        # LagouSpider,
        # BossSpider,
        # LiepinSpider,
        # JDSpider,
        # DoubanSpider,
        # BBSSpider,
        # ZhiLianSpider,
        # AmazonCnSpider,
    ]

    process_list = []
    for validator in validators:
        popen = subprocess.Popen(
            ['python', 'run_spider.py', validator], shell=False)
        data = {
            'name': validator.name,
            'popen': popen,
        }
        process_list.append(data)


if __name__ == '__main__':
    os.chdir(sys.path[0])

    if not os.path.exists('log'):
        os.makedirs('log')

    logging.basicConfig(
        filename='log/validator.log',
        format='%(asctime)s: %(message)s',
        level=logging.DEBUG
    )

    validator()
