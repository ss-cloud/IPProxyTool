# -*- coding: utf-8 -*-

import sys
import logging
import config
import pymongo

from optparse import OptionParser
from sql import SqlManager
from proxy import Proxy


class DataProces(object):

    def __init__(self, file, verbose=False):
        self.file = file
        self.verbose = verbose
        self.sql = SqlManager()
        if not self.verbose:
            self._init_log()
        else:
            logging.disable(sys.maxint)

    def _init_log(self):
        # init logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='log/export.log',
                            filemode='w')

        #######################################################################
        #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def doimport(self):
        infile = open(self.file, 'r')
        lines = infile.readlines()
        total = len(lines)
        index = 0
        for line in lines:
            index = index + 1
            ipport = line.split(':')
            if len(ipport) != 2:
                continue
            ip = ipport[0]
            port = ipport[1]

            proxy = Proxy()
            proxy.set_value(
                ip=ip,
                port=port,
                country='None',
                anonymity='None',
                source='dataproces',
            )
            logging.info('[%d/%d]proxy:%s' % (index, total, proxy.get_dict()))
            self.sql.insert_proxy(config.free_ipproxy_table, proxy)

    def doexport(self):
        out = open(self.file, 'w')
        query = {
            'httpbin': True
        }
        proxies = self.sql.db[config.free_ipproxy_table].find(query).sort('httpbin_vali_time', -1)
        for proxy in proxies:
            logging.info(proxy)
            p = "%s:%s\n" % (proxy.get('ip'), proxy['port'])
            out.write(p)
            out.flush()
        out.close()


if __name__ == '__main__':
    usage = """usage: %prog [options] action
    action:
        i import from file;
        e export to file;

    """
    parser = OptionParser(usage=usage)

    parser.add_option("-f", "--file", dest="file", default="log/out.txt",
                      help="import or export's FILE", metavar="FILE")

    parser.add_option("-q", "--quiet", dest="verbose", default=False,
                      help="don't print status messages to stdout")
    (options, args) = parser.parse_args()

    d = DataProces(options.file, options.verbose)
    action = "e"
    if len(args) >= 1:
        action = args[0]

    if action == 'e':
        d.doexport()
    elif action == 'i':
        d.doimport()
