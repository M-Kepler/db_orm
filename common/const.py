# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-23 11:55:03
Filename     : const.py
Description  : 常量定义
"""

import uuid


class Config:
    LOG_LEVEL = "debug"
    LOG_ROOT_DIR = './log/today'


class dbConfig:
    """
    db 相关的配置
    """
    APP = 'huagnjinjie'

    ENTRY = "http://127.0.0.1/call"

    # db 查询操作
    QUERY_OP_SQL = 't_sql'
    # t_list 分页查询结果会省略掉字段名，只有字段的值
    QUERY_OP_LIST = 't_list'

    # db 查询语句结构
    BASE_QUERY_PARAM = {
        'op': QUERY_OP_SQL,
        'app': APP,
        'table': '.',
        'sid': uuid.uuid4().hex,
        'sql': ''
    }

    # 为避免与关键字冲突，db规范使用反引号把冲突字段括起来
    MAGIC_CHAR = "`"

    # 通过db日期区间查询的日期格式，如：20200724
    DATE_FMT = '%Y%m%d'

    # db 应用根路径
    DB_ROOT = '/data/db/db/log_data/store/'

    # db 日期通配符
    TABLE_REG = '[0-9]*'

    # 查询结果集暂存redis的键值
    REDIS_SEC = "db_query_result"

    # 查询结果集暂存redis的生命周期
    REDIS_QUERY_RET_TTL = 1 * 60

    # BLOB 类型原始数据路径
    # 如：/data/db/db/log_data/store/app/blob/test_tb/20200718
    BLOB_ORIGIN_DATA_ROOT = 'blob/{0}/%s'

    # BLOB 类型数据经过db建立索引后的路径
    # 如：/data/db/db/log_data/store/app/blob/table/test_tb/20200718/test_tb
    BLOB_INDEX_ROOT = 'blob/table/{0}/%s/{0}'

    # db 最大支持查询100w的数据
    MAX_LIMIT = 1000000

    # db 查询时产生临时文件路径
    SQL_TEMP_DIR = "/data/db/db/log_data/_mapreduce/temp/sql/"


class SqlConfig:
    """
    SQL 语句相关配置
    """
    # 关键字
    OPTIONS_AND = " and "
    OPTIONS_OR = " or "
    ORDER_BY = "order by"
    GROUP_BY = "group by"
    LIMIT = "limit"
    BASE_QUERY_SQL = "select %(collector)s %(field)s from "
