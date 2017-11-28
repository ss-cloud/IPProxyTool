# coding=utf-8

DB_config = {
    # 'db_type': 'mongodb',
    'db_type': 'mysql',

    'mysql': {
        'host': '47.92.53.161',
        'port': 3307,
        'user': 'root',
        'password': 'Zanxing$2016',
        'charset': 'utf8',
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'password': '123456',
        'db': 1,
    },
    'mongodb': {
        'host': 'localhost',
        'port': 27017,
        'username': '',
        'password': '',
    }
}

database = 'ipproxy'
free_ipproxy_table = 'free_ipproxy'
httpbin_table = 'httpbin'

data_port = 8000
