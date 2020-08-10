# -*-coding:utf-8-*-


class DapConfig:
    '''
        DAP 相关的配置
    '''
    ENTRY = "http://127.0.0.1:1087/call"

    # 为避免与关键字冲突，DAP规范使用反引号把冲突字段括起来
    MAGIC_CHAR = "`"

    # 通过DAP日期区间查询的日期格式，如：20200724
    DATE_FMT = '%Y%m%d'

    # DAP应用BBC的根路径
    BBC_ROOT = '/sf/db/dap/log_data/store/bbc/'

    # DAP 日期通配符
    TABLE_REG = '[0-9]*'

    # 查询结果集暂存redis的键值
    REDIS_SEC = "dap_query_result"

    # 查询结果集暂存redis的生命周期
    REDIS_QUERY_RET_TTL = 1 * 60

    # BLOB类型原始数据路径
    # 如：/sf/db/dap/log_data/store/bbc/blob/bestext/20200718
    BLOB_ORIGIN_DATA_ROOT = 'blob/{0}/%s'

    # BLOB类型数据经过DAP建立索引后的路径
    # 如：/sf/db/dap/log_data/store/bbc/blob/table/bestext/20200718/bestext
    BLOB_INDEX_ROOT = 'blob/table/{0}/%s/{0}'

    # DAP最大支持查询100w的数据
    MAX_LIMIT = 1000000


class SqlConfig:
    '''
        SQL 语句相关配置
    '''
    # 关键字
    OPTIONS_AND = " and "
    OPTIONS_OR = " or "
    ORDER_BY = "order by"
    GROUP_BY = "group by"
    LIMIT = "limit"
    BASE_QUERY_SQL = "select %(collector)s %(field)s from "
