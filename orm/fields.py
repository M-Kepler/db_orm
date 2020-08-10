# -*-coding:utf-8-*-

'''
表字段所映射的对象
Field子类可以扩展做字段验证、类型转换、设置默认值等
+-------------------+---------------+----------------------+-----------+
| Field             | Type          |                      | Field     |
+-------------------+---------------+----------------------+-----------+
| id                | int(11)       | ---映射到Field类----> | Field子类 |
| branch_id         | int(11)       | ---映射到Field类----> | Field子类 |
+-------------------+---------------+----------------------+-----------+
'''

from abc import ABCMeta, abstractproperty

from ..transformers.converters import IntegerConverter
from ..transformers.converters import StringConverter
from ..transformers.converters import DatetimeConverter


class BaseField(object):
    '''字段类型的抽象基类
       定义了抽象属性dap_field，子类必须实现该方法
    '''

    __metaclass__ = ABCMeta

    def __init__(self, name, column_type, default, comment):
        '''
        :param name 字段名
        :param column_type 字段类型
        :param default 默认值
        :param comment 字段说明
        '''
        self.name = name
        self.column_type = column_type
        self.default = default
        self.comment = comment

    def __str__(self):
        return '<%s, %s:%s, %s>' % (self.__class__.__name__,
                                    self.column_type,
                                    self.name,
                                    self.comment)

    @abstractproperty
    def dap_field(self):
        '''经过DAP提取器装饰后的字段'''
        pass


class IntegerField(BaseField):
    def __init__(self, name, culomn_type="int", default=0, comment=""):
        super(IntegerField, self).__init__(name, culomn_type, default, comment)

    @property
    def dap_field(self):
        return IntegerConverter(self.name).value


class StringField(BaseField):
    def __init__(self, name=None, column_type='varchar(1024)', default="", comment=""):
        super(StringField, self).__init__(name, column_type, default, comment)

    @property
    def dap_field(self):
        return StringConverter(self.name).value


class DataTimeFile(BaseField):
    def __init__(self, name=None, default=None, column_type='varchar(100)', comment=""):
        super(DataTimeFile, self).__init__(name, column_type, default, comment)

    @property
    def dap_field(self):
        return DatetimeConverter(self.name).value