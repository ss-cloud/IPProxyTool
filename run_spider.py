# -*- coding: utf-8 -*-

import os
import logging
import sys


def runspider(validator):
    logging.basicConfig(
        filename='log/%s.log' % validator.name,
        format='%(levelname)s %(asctime)s: %(message)s',
        level=logging.DEBUG
    )
    v = validator()
    v.start_requests()

    logging.debug('finish this spider:%s\n\n' % name)


if __name__ == '__main__':
    try:
        name = sys.argv[1] or 'base'
        runspider(name)
    except Exception as e:
        logging.exception('run_spider main exception msg:%s' % e)
