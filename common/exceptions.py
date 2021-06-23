# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-23 11:54:31
Filename     : exceptions.py
Description  : 异常处理模块，一个类一个异常
"""

from ..common.log import getLogger
from ..i18n.ui import gettext as _

LOG = getLogger(__name__)
MODULE_NAME = "db_orm.common.exceptions"


class dbOrmBaseException(Exception):
    _ERR_MSG = "unknow_exception"

    def __init__(self, message, **kwargs):
        if not message:
            message = self._ERR_MSG
        try:
            if kwargs:
                message = message % kwargs
        except Exception as ex:
            LOG.exception(ex)
            raise ex
        self.message = message
        super(dbOrmBaseException, self).__init__(message)


class GetOriginalDataFailed(dbOrmBaseException):
    _ERR_MSG = _("%s$$get_original_data_failed" % MODULE_NAME)

    def __init__(self):
        super(dbOrmBaseException, self).__init__(message=self._ERR_MSG)


class dbModelFieldsNotFound(dbOrmBaseException):
    _ERR_MSG = _("%s$$db_module_fields_not_found" % MODULE_NAME)

    def __init__(self, table, fields):
        super(dbOrmBaseException, self).__init__(message=self._ERR_MSG,
                                                  table=table,
                                                  fields=fields)


class dbModelFilterNotFound(dbOrmBaseException):
    _ERR_MSG = _("%s$$db_module_filter_not_found" % MODULE_NAME)

    def __init__(self, _filter):
        super(dbOrmBaseException, self).__init__(message=self._ERR_MSG,
                                                  filter=_filter)


class dbQueryParamErr(dbOrmBaseException):
    _ERR_MSG = _("%s$$db_query_param_err" % MODULE_NAME)

    def __init__(self):
        super(dbOrmBaseException, self).__init__(message=self._ERR_MSG)


class dbModelFilterValueErr(dbOrmBaseException):
    _ERR_MSG = _("%sdb_module_filter_value_err" % MODULE_NAME)

    def __init__(self, expect, got_value):
        LOG.exception(
            "db_module_filter_value_err, expect: [%s], got: [%s]" % expect,
            got_value)
        super(dbOrmBaseException, self).__init__(message=self._ERR_MSG,
                                                  expect=expect,
                                                  got_value=got_value)
