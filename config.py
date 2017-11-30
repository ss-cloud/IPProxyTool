# coding=utf-8

DB_config = {
    # 'db_type': 'mongodb',
    'db_type': 'mongodb',

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
        'host': '47.92.53.161',
        'port': 27017,
        'username': 'githubseo',
        'password': 'Zanxing$2017',
        'db': 'githubseo',
    }
}

database = 'githubseo'
free_ipproxy_table = 'freeproxy'
httpbin_table = 'httpbin'

data_port = 8000
thread_num = 500
