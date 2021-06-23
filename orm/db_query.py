# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-12 12:11:52
Filename     : db_query.py
Description  : 
"""

import os
import json
import requests

from ..common.log import getLogger
from ..common.const import DBConfig
from ..common.exceptions import GetOriginalDataFailed

LOG = getLogger(__name__)


class DBUtils(object):
    def __init__(self):
        pass

    @classmethod
    def clear_db_query_cache(cls, sid):
        """
        清理 db 查询过程中的缓存文件，以免频繁查询堆积大量垃圾文件

        临时文件目录如下：
        /data/db/db/log_data/_mapreduce/temp/sql/597/61b01906c39940ec962ba379008f8b2b
            12673/  J1/  progress/
        # 查询完把 /data/db/db/log_data/_mapreduce/temp/sql/597 目录删掉

        :param sid db 查询ID
        """
        try:
            if not sid:
                return
            for root, _, _ in os.walk(DBConfig.SQL_TEMP_DIR):
                if root.endswith(sid):
                    os.removedirs(os.path.dirname(root))
                    break
        except Exception as ex:
            LOG.debug("delete db query cache dir %s failed: %s" % (sid, ex))

    @classmethod
    def do_query(cls, query_param, clear_cache=True):
        """
        :desc
            向 db 的 restful 查询接口发请求，获取数据
            完成向DB查询的操作
        :param query_param
            查询参数，格式为
            {
                "op": "t_sql",
                "table": ...,
                "sql": ...,
                "app": ...,
                "sid": 指定SQL查询的ID，通过此ID可以跟踪查询进度或者取消查询
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
        :param clear_cache 是否清空查询缓存
               t_list 分页查询模式下，需要保留缓存文件供分页
        :return
            查询到的数据，失败则抛异常 GetOriginalDataFailed
        """
        # LOG.debug("db query param:[%s]" % query_param)

        try:
            resp = requests.post(DBConfig.ENTRY, params=query_param)
            if resp.status_code >= 400:
                LOG.error("Request [%s:%s] failed: %s" %
                          ("POST", DBConfig.ENTRY, resp.content))
                raise GetOriginalDataFailed()

            resp_dict = json.loads(resp.content)
            if resp_dict["code"] != 0:
                LOG.warn(resp_dict.get("message", ""))
            return resp_dict["data"]
        except Exception as ex:
            LOG.exception(ex)
            raise GetOriginalDataFailed()
        finally:
            if clear_cache:
                cls.clear_db_query_cache(sid=query_param.get('sid'))
