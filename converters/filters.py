# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-12 12:11:29
Filename     : filters.py
Description  : 查询过滤器

原SQL：
    select dept from report where event_type in (1, 2) and device_id = 5;
DB SQL:
    # where语句用and/or连接前要用加上括号，有需要的话要给字段套上过滤器
    select dept from report where (include(event_type) in (1, 2)) and (device_id = 5);
"""

from abc import ABCMeta, abstractproperty
from ..common.exceptions import DBModelFilterValueErr


class BaseFilter(object):
    """
    过滤器抽象基类

    定义了抽象属性filter，子类必须实现该方法
    """

    __metaclass__ = ABCMeta

    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.field,
                                self.value)

    @abstractproperty
    def filter(self):
        """
        经过DB提取器装饰后的字段
        """
        pass


class IncludeFilter(BaseFilter):
    def __init__(self, field, value):
        super(IncludeFilter, self).__init__(field, value)

    @property
    def filter(self):
        if not isinstance(self.value, list):
            raise DBModelFilterValueErr(expect=tuple,
                                         got_value=type(self.value))
        return 'include(%s) in %s' % (self.field, str(tuple(self.value)))


class EqFilter(BaseFilter):
    def __init__(self, field, value):
        super(EqFilter, self).__init__(field, value)

    @property
    def filter(self):
        return 'eq(%s) = %s' % (self.field, self.value)
