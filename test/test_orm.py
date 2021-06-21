# -*-coding:utf-8-*-

import time as _time
import unittest
from functools import wraps

from ..common.const import DapConfig
from ..orm.orm import Model
from ..orm.fields import IntegerField
from ..orm.fields import StringField
from ..converters.filters import IncludeFilter, EqFilter
from ..common.exceptions import DapModelFieldsNotFound
from ..common.exceptions import DapModelFilterNotFound
from ..common.exceptions import DapModelFilterValueErr
from ..common.exceptions import DapQueryParamErr
from ..orm.tables import BestExt


class TestBestExt(unittest.TestCase):
    # table_date = datetime.today().strftime('%Y%m%d')
    table_date = 20200817

    # 是否把用例结果输出
    OUTPUT = False

    # 跳过的用例：跳过原因
    SKIP_CASE = {
        # 'test_query_param_err': "测试查询语句错误",
        # 'test_query_with_date': "指定日期查询测试",
        # 'test_query_with_date_range': "指定日期区间查询测试",
        # 'test_query_without_date': "不指定查询测试",
        # 'test_unknow_field': "测试所查询的字段是否存在",
        # 'test_unknow_filter': "测试查询使用了未知的过滤器",
        # 'test_unmatch_field_type': "测试查询所用过滤器与传入的查询值类型不匹配",
        # 'test_filter': "测试条件查询",
        # 'test_set_unknow_field': '测试给Model绑定不属于表字段的属性',
        # 'test_limit': "测试限制返回数量",
        # 'test_getall': "测试获取全部数据",
        # 'test_getfirst': "测试获取一条数据",
        # 'test_count': "测试获取查询结果条目数量",
        # 'test_sum': "测试sum 语句",
        # 'test_order_by': "测试 order by 语句",
        # 'test_order_by_desc': "测试 倒序 语句",
        # 'test_order_by_asc': "测试 正序 语句",
        # 'test_unit_query': "测试多个查询条件拼接",
        # 'test_per_page': "测试分页查询",
        # 'test_group_by': "测试group by 语句"
    }

    # 查询条件
    where_args = [
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

    def unittest_case(func):
        # 装饰器，根据TEST_CASE来指定哪些用例需要执行
        # 否则需要执行/取消某几个用例时要到每个函数加上/取消装饰器，太麻烦
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if func.func_name in self.SKIP_CASE.keys():
                print('skip func [%s] for reason [%s]' %
                      (func.func_name, self.SKIP_CASE.get(func.func_name)))
                return
            begin = _time.strftime('%Y-%m-%d %H:%M:%S', _time.localtime(_time.time()))
            print('【start func %s at %s' % (func.func_name, begin))
            func(self, *args, **kwargs)
            end = _time.strftime('%Y-%m-%d %H:%M:%S', _time.localtime(_time.time()))
            print(' end at %s】\n' % end)

        return wrapper

    @classmethod
    def setUpClass(cls):
        pass

    @unittest_case
    def test_query_with_date_range(self):
        ret = BestExt.query(start_date=20200711, end_date=20200721).all()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_query_with_date(self):
        ret = BestExt.query(tb_date=self.table_date).all()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_query_without_date(self):
        ret = BestExt.query().all()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_unmatch_field_type(self):
        where_args = [
            {
                "field": "event_type",
                "value": 2,
                "filter": IncludeFilter
            }
        ]

        with self.assertRaises(DapModelFilterValueErr):
            BestExt.query(tb_date=self.table_date).filter(where=where_args).all()

    @unittest_case
    def test_unknow_field(self):
        where_args = [
            {
                "field": "event_typexxx",
                "value": (1, 2),
                "filter": IncludeFilter
            }
        ]

        with self.assertRaises(DapModelFieldsNotFound):
            BestExt.query(tb_date=self.table_date).filter(where=where_args).all()

    @unittest_case
    def test_unknow_filter(self):
        class IncludeFilterxxx:
            pass

        where_args = [
            {
                "field": "event_type",
                "value": (1, 2),
                "filter": IncludeFilterxxx
            }
        ]
        with self.assertRaises(DapModelFilterNotFound):
            BestExt.query(tb_date=self.table_date).filter(where=where_args).all()

    @unittest_case
    def test_filter(self):
        ret = BestExt.query(tb_date=self.table_date).filter(
            where=self.where_args).all()
        if self.OUTPUT:
            for item in ret:
                for k, v in item.items():
                    print('%s: \t%s' % (k, v))
                print('\n')

    @unittest_case
    def test_limit(self):
        ret = BestExt.query(tb_date=self.table_date).limit(3).all()
        if self.OUTPUT:
            for item in ret:
                for k, v in item.items():
                    print('%s: \t%s' % (k, v))
                print('\n')
        if ret:
            self.assertEqual(3, len(ret))

    @unittest_case
    def test_getall(self):
        ret = BestExt.query().all()
        if self.OUTPUT:
            for item in ret:
                for k, v in item.items():
                    print('%s: \t%s' % (k, v))
                print('\n')

    @unittest_case
    def test_getfirst(self):
        ret = BestExt.query(tb_date=self.table_date).first()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_count(self):
        ret = BestExt.query().count()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_sum(self):
        ret = BestExt.query(tb_date=self.table_date).sum('device_id')
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_order_by(self):
        ret = BestExt.query(
            tb_date=self.table_date).order_by('occur_time').all()
        # a >= b
        if len(ret) > 2:
            self.assertGreaterEqual(int(ret[0].occur_time), int(ret[2].occur_time))

    @unittest_case
    def test_unit_query(self):
        ret = BestExt.query(
            tb_date=self.table_date).limit(1).order_by('occur_time').all()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_set_unknow_field(self):
        with self.assertRaises(AttributeError):
            a = BestExt()
            a.device_id2 = 1

    @unittest_case
    def test_per_page(self):
        curr_page = 1
        page_size = 2
        mdd_path = None
        mdd_path, first_page_result = BestExt.query().limit(page_size).offset(
            page_num=curr_page, mdd_path=mdd_path)
        for item in first_page_result['data']:
            print(BestExt._format_dap_item(item))

        mdd_path, second_page_result = BestExt.query().limit(page_size).offset(
            page_num=curr_page + 1, mdd_path=mdd_path)
        for item in second_page_result['data']:
            print(BestExt._format_dap_item(item))

    @unittest_case
    def test_group_by(self):
        ret = BestExt.query().group_by('device_id', 'occur_time').all()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_order_by_desc(self):
        ret = BestExt.query(
            tb_date=self.table_date).order_by('occur_time').desc()
        if self.OUTPUT:
            print(ret)
        # a >= b

    @unittest_case
    def test_order_by_asc(self):
        ret = BestExt.query(
            tb_date=self.table_date
        ).order_by(
            field='occur_time'
        ).asc()
        if self.OUTPUT:
            print(ret)

    @unittest_case
    def test_query_param_err(self):
        with self.assertRaises(DapQueryParamErr):
            BestExt.query(tb_date=self.table_date).desc()


if __name__ == "__main__":
    unittest.main()
