# -*-coding:utf-8-*-

"""
Author       : M_Kepler
EMail        : m_kepler@foxmail.com
Last modified: 2021-06-12 12:11:04
Filename     : combiners.py
Description  : 查询聚合器
原SQL：
    select sum(device_id) from report
DB SQL:
    select sum(device_id) device_ids from report
"""

from abc import ABCMeta, abstractproperty
from ..common.const import DBConfig


class BaseCombiner(object):
    """
    聚合器抽象基类

    定义了抽象属性filter，子类必须实现该方法
    """

    __metaclass__ = ABCMeta

    def __init__(self, field=None):
        """
        :param field 字段名
        """
        self.field = field

    def __str__(self):
        return '<%s, %s>' % (self.__class__.__name__, self.field)

    @abstractproperty
    def combiner(self):
        """
        DB聚合器修饰后的查询

        DB聚合器查询结果值不能与关键字同名（原始sql是可以的）
        比如 select sum(device_id) sum from 20200716 查询会报错
        """
        pass


class CountCombiner(BaseCombiner):
    """
    计数聚合器

    - `count()` 聚合器的意义与原始 `sql` 有歧义
    - 原始 `sql`
        select count(1) from report;
        select count(id) from report;
        # 两个语句都表示表中有多少条数据

        # 所有id值求和
        select sum(id) from report;

    - `DB` 的 `sql`
        # 表示的是 `report` 表中所有的`device_id` 的总和
        # 即 `sum` 的意思，但是 `db` 已经有 `sum` 来支持计算统计了
        select count(device_id) device_ids from report;
        # 等价于
        select sum(device_id) device_ids from report;

        # 表示的才是表中有多少条数据
        select count(1) from report;
    """
    def __init__(self):
        super(CountCombiner, self).__init__()

    @property
    def combiner(self):
        # 与关键字 count 冲突，需要用 ` 括起来
        return 'count(1) {0}count{0}'.format(DBConfig.MAGIC_CHAR)


class SumCombiner(BaseCombiner):
    def __init__(self, field="%s"):
        """
        查询聚合器也可以实例化的时候指定需要聚合的字段field，但是不建议这样做

        在orm.py的元类 ModelMateclass中，会构建一系列默认的SQL语句作为类属性
            cls_attrs['__sum__'] = cls_attrs['__base_sql__'] % SumCombiner().combiner
        实例化类的时候直接给这些属性传参就行了
            cls.__sum__.format(field)
        详见orm.py中的使用
        """
        super(SumCombiner, self).__init__(field)

    @property
    def combiner(self):
        if self.field != "%s":
            return 'sum({0}) {0}s'.format(self.field)
        else:
            return 'sum({0}) {0}s'
