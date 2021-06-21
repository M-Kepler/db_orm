# -*-coding:utf-8-*-

'''
处理DAP表数据的ORM框架
映射DAP表模型为类，支持查询、过滤等sql操作

DAP 参考文档
http://dap.pr.sangfor.org/index.php?s=/2&page_id=70
http://dap.pr.sangfor.org/index.php?s=/7&page_id=106
'''

import os
import copy
from operator import itemgetter

from ..common.log import getLogger

from .dap_query import DapUtils
from .fields import BaseField
from ..common.const import DapConfig
from ..common.const import SqlConfig
from ..converters.filters import BaseFilter
from ..converters.combiners import CountCombiner
from ..converters.combiners import SumCombiner
from ..converters.collectors import DateCollector

from ..common.exceptions import DapModelFieldsNotFound
from ..common.exceptions import DapModelFilterNotFound
from ..common.exceptions import DapQueryParamErr


LOG = getLogger(__name__)


class ModelMetaclass(type):
    '''
    :desc
        定义元类，把表映射成类，表字段作为类的属性
    '''
    def __new__(cls, cls_name, cls_bases, cls_attrs):
        '''
        :desc
            重写 __new__ 方法，自定义类的创建
        '''
        dap_fields = list()
        attr_map = dict()

        # Model是基类，需要排除对Model类的修改
        if cls_name == 'Model':
            return type.__new__(cls, cls_name, cls_bases, cls_attrs)

        # 因为 t_list 查询模式返回结果只包含值，没有字段名
        # 所以，查询的字段顺序按字母顺序排一下序，以免下标取值出错
        for k, v in sorted(cls_attrs.items()):
            if isinstance(v, BaseField):
                # LOG.debug('found mapping: %s ==> %s' % (k, v))
                # 保存属性和列的映射关系
                attr_map[k] = v
                # 取类属性对应的Field子类处理后的值，经过DAP提取器处理之后的字段
                dap_fields.append(v.dap_field)

        # 元类自身的属性需要清除，以免覆盖子类的属性
        for k in attr_map:
            cls_attrs.pop(k)

        cls_attrs['__table__'] = cls_attrs.get('__table__', cls_name)
        cls_attrs['__sort_by__'] = cls_attrs.get('__sort_by__')
        cls_attrs['__fields__'] = dap_fields
        cls_attrs['__mappings__'] = attr_map
        cls_attrs['__slots__'] = tuple(attr_map.keys())

        # 构造默认的SQL语句
        # 因为DAP把目录当成表，不同查询条件，表不一样
        # 所以SQL语句中不指定查询表为 __table__

        # 构造基本查询语句（默认查询表的全部字段） [select device_id, occur_time from ]
        # 也可以使用字符串拼接的方式，但是拼接的方式器看起来不清晰
        # cls_attrs['__select__'] = SqlConfig.BASE_QUERY_SQL % ', '.join(dap_fields)
        cls_attrs['__select__'] = SqlConfig.BASE_QUERY_SQL % {
            "collector": "%(collector)s",
            "field": ', '.join(dap_fields)
        }
        '''
        # 构造可以包含指定收集器的查询语句 [select %s device_id, occur_time from ]
        # 因为收集器也是根据查询需要来制定的，所以用 %(collector)s作为占位符
        '''
        # 构造包含聚合器的查询语句 [select count(1) `count` from ]
        cls_attrs['__count__'] = SqlConfig.BASE_QUERY_SQL % {
            "collector": "",
            "field": CountCombiner().combiner
        }
        # 构造包含求和聚合器的查询语句 [select sum({0}) {0}s from ]
        # 因为需要求和的字段是传进来的，所以构造的使用用 {0} 做占位
        cls_attrs['__sum__'] = SqlConfig.BASE_QUERY_SQL % {
            "collector": "",
            "field": SumCombiner().combiner
        }

        return type.__new__(cls, cls_name, cls_bases, cls_attrs)


class Model(dict):
    '''
    :desc
        根据元类定义表模型
    '''
    __metaclass__ = ModelMetaclass

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        '''
        :desc
            设置类属性
            __slots__属性只能放在子类中，这样每次定义表都要写__slots__
            所以在父类中进行限制，设置属性时，如果字段不存在，则抛异常
        '''
        if key not in self.__slots__:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
        self[key] = value

    @classmethod
    def _make_where_sql(cls, options=SqlConfig.OPTIONS_AND, where=None):
        '''
        :desc
            拼接sql语句
        :param  options
            查询条件之间的连接词，与 and / 或 or
        :param  where
            - 所查询表的字段和值组成的字典
                where = [
                    {
                        "filed": "event_type",
                        "value": (1, 2),
                        "filter": IncludeFilter
                    }
                    {
                        "filed": "device_id",
                        "value": "1",
                        "filter": EqFilter
                    }
                ]
            - 查询参数够着得有点奇葩，但也是无奈之举，DAP有一个叫过滤器的东西，需要对查询的字段做一番转换
            - 构建这样的查询结构，可以校验查询的字段 field 是否存在，对查询的值 value 做格式判断，
              比如对于IncludeFilter，值应该是tuple类型，filter表示过滤器

        :return
        where ('incude(event_type in %{event_type}s)') and ('eq(device_id=%{device_id}s)')
        '''
        # 组装所有字段的where语句格式
        if where is None:
            return ""
        tmp_where = list()
        for item in where:
            if not issubclass(item['filter'], BaseFilter):
                raise DapModelFilterNotFound(_filter=item['filter'])
            tmp_where.append(
                '(' + item['filter'](item['field'], item['value']).filter + ')'
            )
        return ' where ' + options.join(tmp_where)

    @classmethod
    def _make_query_sql(cls, params):
        '''拼接SQL语句
        '''
        # params['sql'] += params['table']

        # 拼接 where 语句
        if params.get('where'):
            params['sql'] += cls._make_where_sql(params['options'], params['where'])
            params.pop('where')

        # 拼接 order by 语句
        if params.get(SqlConfig.ORDER_BY):
            params['sql'] += ' %s ' % SqlConfig.ORDER_BY + params[SqlConfig.ORDER_BY]

        # 拼接 group by 语句
        if params.get('sort'):
            params['sql'] = " ".join([
                params['sql'],
                params['sort']
            ])

        if params.get(SqlConfig.GROUP_BY):
            params['sql'] += ' %s ' % SqlConfig.GROUP_BY + params[SqlConfig.GROUP_BY]

        return params

    @classmethod
    def all(cls):
        '''
        :desc
            执行查询操作
            DAP不支持全部查询数据，而且最大只支持查询出100万的数据
            查询中如果不加 limit 参数，会默认只返回 1000 条数据
            为了支持查询全部数据，手动设置 limit 参数为100w
        :return
            返回查询结果为Model子类组成的列表
        '''
        # Model继承自dict类，可以直接用**r给类属性赋值
        if SqlConfig.LIMIT not in cls.query_param:
            cls.query_param.update({SqlConfig.LIMIT: DapConfig.MAX_LIMIT})
        query_params = cls._make_query_sql(cls.query_param)
        query_ret = DapUtils.do_query(query_params)
        return [cls(**r) for r in query_ret] if query_ret else []

    @classmethod
    def first(cls):
        '''
        :desc
            执行查询操作
        :return
            返回查询结果为查询到的一个Model子类
        '''
        query_params = cls._make_query_sql(cls.query_param)
        query_ret = DapUtils.do_query(query_params)
        return cls(**(query_ret[0])) if query_ret else None

    @classmethod
    def count(cls):
        '''返回记录总数
        [
            {
                "$ID": 1,
                "count": "858"
                # 这个字段在 combiners.py 中指定了
            }
        ]
        '''
        cls.query_param.update({"sql": cls.__count__ + cls._make_query_table()})
        query_params = cls._make_query_sql(cls.query_param)
        query_ret = DapUtils.do_query(query_params)
        return query_ret[0].get('count') if query_ret else 0

    @classmethod
    def sum(cls, field):
        '''对64位整数集合求和
        [
            {
                "$ID": 1,
                "device_ids": "806"
            }
        ]
        '''
        if field not in cls.__mappings__:
            raise DapModelFieldsNotFound(cls.__table__, field)

        cls.query_param.update({
            "sql": (cls.__sum__.format(field)) + cls._make_query_table()})

        query_params = cls._make_query_sql(cls.query_param)
        query_ret = DapUtils.do_query(query_params)
        # SumCombiner 聚合器指定了查询返回结果存放到 field + 's' 字段中
        ret = query_ret[0].get(field + 's') if query_ret else 0
        return ret

    @classmethod
    def asc(cls):
        '''
        :desc
            XXX 正序查询 从小到大
            DAP 仅支持 select f1, blob_pos from 20180806:aci order by f1 limit 15
                这种对指定数量的数据做排序的查询，无法真正做到全表排序
                这样会存在一个问题，比如查询18条数据，那么后面3条数据顺序是未知的
            XXX 这种在order by 后添加 asc 的方法DAP貌似支持
            文档路径：http://dap.pr.sangfor.org/index.php?s=/7&page_id=203
        '''
        # 必须先order by再进行排序
        if SqlConfig.ORDER_BY not in cls.query_param:
            raise DapQueryParamErr()
        cls.query_param.update({"sort": "asc"})
        query_ret = cls.all()
        query_ret.sort(key=itemgetter(cls.query_param.get(SqlConfig.ORDER_BY)),
                       reverse=False)
        return query_ret

    @classmethod
    def desc(cls):
        '''
        :desc 倒序排序 从大到小
        '''
        # 必须先order by再进行排序
        if SqlConfig.ORDER_BY not in cls.query_param:
            raise DapQueryParamErr()
        cls.query_param.update({"sort": "desc"})
        query_ret = cls.all()
        query_ret.sort(key=itemgetter(cls.query_param.get(SqlConfig.ORDER_BY)),
                       reverse=True)
        return query_ret

    @classmethod
    def _make_query_table(cls, date_range=False):
        '''
        :desc
            拼接SQL查询表

        :param tb_date
            查询日期
        :return query_table
            XXX 没有找到文档，查看DAP文档的例子发现的用法
            指定日期，则返回 'blob:table:bestext:20200717:bestext'
            指定日期范围，则返回 '`blob/table/bestext/[0-9]*/bestext,20200710-20200718`'
            不指定日期，则返回 '`blob/table/bestext/[0-9]*/bestext`'
        '''
        if cls.tb_date:
            query_table = ":".join(
                cls.__table__.split('/')
            ) % str(cls.tb_date)
            return query_table
        else:
            query_table = "".join([
                DapConfig.MAGIC_CHAR,
                cls.__table__ % DapConfig.TABLE_REG,
                "/%s",  # 留个位置来填查询的日期区间
                DapConfig.MAGIC_CHAR
            ])
            return query_table % (',' + '-'.join([str(cls.start_date), str(cls.end_date)]) if date_range else "")

    @classmethod
    def query(cls, start_date=None, end_date=None, tb_date=None):
        '''
        :desc
            组装基本的查询参数
            参考DAP文档:
            http://dap.pr.sangfor.org/index.php?s=/7&page_id=106

        :param tb_date
            DAP把数据按照上报日期存放到日期文件夹中，每个文件夹都认为是一张表
            1. 指定日期          传入 20200710 格式的日期
        :param start_date, end_date
            2. 指定日期范围       传入 20200701-20200710的日期
        :param
            不传入参数则查询全部
        :return cls
            返回类本身
        '''
        cls.tb_date = tb_date
        cls.start_date = start_date
        cls.end_date = end_date

        date_range = False
        collector = ""
        if cls.start_date and cls.end_date:
            # 指定使用日期收集器
            date_range = True
            collector = DateCollector().collector
        cls.__select__ = cls.__select__ % {
                "collector": collector
            }
        # query_param 不要放在元类中
        # 否则上次查询的参数会留在类里面，影响下次查询
        cls.query_param = copy.deepcopy(DapConfig.BASE_QUERY_PARAM)
        cls.query_param.update({
            'sql': cls.__select__ + cls._make_query_table(date_range)})
        LOG.info("query_param:%s" % cls.query_param)
        return cls

    @classmethod
    def filter(cls, where=None, options=SqlConfig.OPTIONS_AND):
        '''
        :desc
            组装where语句，只修改cls.param，只有在调用all和first的时候才真正去查询
            目的是为了支持组装多个查询语句，比如 CLASSA.filter(xx).limit(xx).all()
        :param where
            查询条件
                where = [
                    {
                        "field": "event_type",
                        "value": [1, 2],
                        "filter": IncludeFilter
                    },
                    {
                        "field": "device_id",
                        "value": 26,
                        "filter": EqFilter
                    }
                ]
        :param options
            字段之间与/或查询
        :return cls
            返回类本身
        '''
        # 检查where语句中的字段是否属于表字段
        if where is not None:
            where_fieds = [x['field'] for x in where]
            delta_fields = set(where_fieds) - set(cls.__mappings__.keys())
            if delta_fields:
                raise DapModelFieldsNotFound(cls.__table__, delta_fields)

        cls.query_param.update({'where': where, 'options': options})
        return cls

    @classmethod
    def order_by(cls, field):
        '''
        :desc
            组装 order by 语句
        :param field
            排序的字段
        :return
            返回类本身
        '''
        # 检查排序字段是否存在
        if field not in cls.__mappings__:
            raise DapModelFieldsNotFound(cls.__table__, field)

        cls.query_param.update({SqlConfig.ORDER_BY: field})
        return cls

    @classmethod
    def group_by(cls, *fields):
        '''
        :desc
            组装 group by 语句
        :param *fields
            多个字段
        :return
            类本身
        '''
        # group by 语句不允许出现在order by 之前
        # XXX 这种做SQL语句检查的方式不太妥
        if SqlConfig.ORDER_BY in cls.query_param:
            raise DapQueryParamErr()

        # 判断group by的字段是否存在
        delta_fields = set(fields) - set(cls.__mappings__.keys())
        if delta_fields:
            raise DapModelFieldsNotFound(cls.__table__, delta_fields)

        field_cnt = len(fields)

        # 传进来的参数是字段，由于字段数量不确定，所以使用 '%s %s %s' % ('device_id', 'occur_time')
        cls.query_param.update({SqlConfig.GROUP_BY: " %s " * field_cnt % fields})
        return cls

    @classmethod
    def limit(cls, limit=None):
        '''
        :desc
            组装 limit 语句
        :param limit
            限制最终结果集的条数，DAP默认最多返回1000条记录
            FIXME 如何查询出全部数据？
        :return
            返回类本身
        '''
        if limit is not None:
            cls.query_param.update({SqlConfig.LIMIT: int(limit)})
        return cls

    @classmethod
    def _offset_query(cls, mdd_path, page_num, page_size):
        """在一个类里面多次调用offset方法，不用多次查询mdd路径

        把查询分页数据的方法抽出来

        Params:
            mdd_path: - mdd 文件分区路径
            page_num: - 页下标
            page_size: - 每页大小

        Returns:
            return value.

        Raises:
            KeyError: raises key exception.
        e.g.:

        pass
        """
        # 使用 t_list 查询模式，分页获取大结果集，返回[begin, end] 闭区间的数据
        cls.query_param.update({
            'op': DapConfig.QUERY_OP_LIST,
            'path': mdd_path,
            'begin': (page_num - 1) * page_size + 1,
            'end': page_num * page_size
        })
        query_ret = DapUtils.do_query(query_param=cls.query_param,
                                      clear_cache=False)
        return query_ret

    @classmethod
    def offset(cls, page_num, mdd_path=None):
        """支持分页查询

        分页查询前，sqlalchemy保持一致，先用limit限定每页数量，在用offset指定页码

        Params:
            page_num: - 页下标

        Returns:
            mdd_path: - mdd 文件路径，方便从同一结果集取下一页
            query_result: - 查询结果

        Raises:
            KeyError: raises key exception.

        e.g.:
            查询第3页的数据，每页大小为 1000
            BestExt.query().limit(1000).offset(3)
        """
        if SqlConfig.LIMIT not in cls.query_param:
            raise DapQueryParamErr()

        page_size = cls.query_param.get(SqlConfig.LIMIT, 0)

        # 指定 limit，否则 dap 默认只能查回 1000 条数据
        cls.query_param.update({SqlConfig.LIMIT: DapConfig.MAX_LIMIT})

        if not mdd_path:
            # 分页查询支持多次调用，不需要每次都取一遍结果集，直接从原有结果集分页取
            # 指定 mdd = 1 ，表示获取结果集路径
            cls.query_param.update({'mdd': 1})
            mdd_path = DapUtils.do_query(
                query_param=cls._make_query_sql(cls.query_param),
                clear_cache=False)

            return mdd_path, cls._offset_query(
                mdd_path=os.path.dirname(mdd_path[0]) if mdd_path else "",
                page_num=page_num,
                page_size=page_size)
        else:
            # 如果已经进行过一次 offset 查询，则直接去结果集取分页数据即可
            return mdd_path, cls._offset_query(mdd_path=mdd_path,
                                               page_num=page_num,
                                               page_size=page_size)
