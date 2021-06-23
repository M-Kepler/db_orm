# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-12 12:10:51
Filename     : collectors.py
Description  : 查询收集器
原SQL：
    select device_id from report where occur_date between (20200710, 20200713)
DB SQL:
    select /* COLLECT:collector.date@core */ device_id from `/path/to/data/[0-9]*/kvd,20180101|20180103-20180409|20180106`
"""

from abc import ABCMeta, abstractproperty


class BaseCollector(object):
    """
    收集器抽象基类

    定义了抽象属性collector ，子类必须实现该方法
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def __str__(self):
        return '<%s>' % (self.__class__.__name__)

    @abstractproperty
    def collector(self, collector):
        pass


class DateCollector(BaseCollector):
    """
    日期收集器
    """
    def __init__(self):
        super(DateCollector, self).__init__()

    @property
    def collector(self):
        return '/* COLLECT:collector.date@core */'
