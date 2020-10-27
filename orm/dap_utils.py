# -*-coding:utf-8-*-

import ast
import json
import uuid
import requests

from ..common.log import getLogger
from ..common.globals import g
# from bbc.redis_tools.common import REDIS
# from bbc.redis_tools.common import PIPE
from ..common.const import DapConfig
from ..common.exceptions import GetOriginalDataFailed

LOG = getLogger(__name__)


class DapUtils(object):
    def __init__(self):
        pass

    @classmethod
    def do_query(cls, http_param):
        """
        :desc
            向 dap 的 restful 查询接口发请求，获取数据
            完成向DAP查询的操作
        :param params
            查询参数，格式为
            {
                "op": "t_sql",
                "table": ...,
                "sql": ...,
                "app": ...
            }
            组装的查询语句如下：
            select i(event_type) event_type,
                   occur_time,
                   s(detail) detail,
                   s(link_id) link_id,
                   s(time) time,
                   s(link_status) link_status,
                   i(device_id) device_id
            from 20200710
            where (event_type=1) and (device_id=5)'
        :return
            查询到的数据，失败则抛异常 GetOriginalDataFailed
        """
        # LOG.debug("dap query param:[%s]" % http_param)

        try:
            resp = requests.post(DapConfig.ENTRY, params=http_param)
            if resp.status_code >= 400:
                LOG.error("Request [%s:%s] failed: %s" %
                          ("POST", DapConfig.ENTRY, resp.content))
                raise GetOriginalDataFailed()

            resp_dict = json.loads(resp.content)
            if resp_dict["code"] != 0:
                LOG.warn(resp_dict.get("message", ""))
            return resp_dict["data"]
        except Exception as ex:
            LOG.exception(ex)
            raise GetOriginalDataFailed()

    @classmethod
    def cache_query_ret(cls, dap_data, sorted_by=None):
        '''
        :desc
            查询结果根据 cls.__sort_by__ 字段排序后存储到redis中
        :param dap_data
            查询到的数据列表，列表元素是Model子类
        :return cls.query_token
            随机ID，把查询结果存储到redis中，指定生命周期，做分也是直接从redis中取
            目的是为了保证分页查询的结果正确性
            比如原有10条数据，按occur_time排序后存储到redis中:(a0, a1, a2, a3, a4.... a9)
            在完成查询与取分页之间又上报了5条数据，其中有一条数据时间较小，则原始数据为
            (a0, a111, a1, a2...a14)，此时再取分页就会取到错误的数据a111
            所以，用redis暂存本次查询的结果
        '''
        if not dap_data:
            query_token = ''
            return
        query_token = str(uuid.uuid4())
        LOG.debug(query_token)
        # 对查询到的数据先做排序，再存到redis中
        # FIXME
        g.query_cache[query_token] = dap_data
        """
        for item in dap_data:
            score = item.get(sorted_by, 0)
            PIPE.zadd(query_token, score, item)
        PIPE.expire(query_token, DapConfig.REDIS_QUERY_RET_TTL)
        PIPE.execute()
        """
        return query_token

    @classmethod
    def get_split_data(cls, query_token, curr_page, page_size):
        '''
        :desc 对数据做分页，获取分页数据
        :param query_token 根据该token获取此次分页操作的查询结果
        :param curr_page 当前页索引
        :param page_size 每页大小
        :return
            返回该页的数据
        '''
        query_return = g.query_cache.get(query_token)
        start = (curr_page - 1) * page_size
        end = curr_page * page_size - 1
        dap_data = query_return[start:end]
        """
        dap_data = REDIS.zrange(name=query_token,
                                start=(curr_page - 1) * page_size,
                                end=curr_page * page_size - 1)
        """
        # 存到 redis 中的json再取出来是这样的: '{u\'event_type\': u\'2\'}' ,没法直接json.loads(xx)
        # 利用ast.literal_eval做解析json字符串
        return [cls(**(ast.literal_eval(x))) for x in dap_data]
