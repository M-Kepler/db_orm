# -*-coding:utf-8-*-
'''
字段提取器
DAP 存储的数据是经过URL编码的，要正常显示需要用提取器进行处理

- 原始sql:
    select event_type, occur_time from tb_name

- DAP的sql
    > 需要对字段套上提取器做解码才能正常显示值
    > 提取器之后的值 event_type 不一定要是字段值，为了避免歧义, 仍然使用字段值表示
    select i(event_type) event_type, s(occur_time) occur_time from tb_name

- 对应DAP 文档:
    http://dap.pr.sangfor.org/index.php?s=/2&page_id=70
'''


from abc import ABCMeta, abstractproperty


class BaseFieldExtractor(object):
    '''字段类型转换器的抽象基类'''
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name

    @abstractproperty
    def value(self):
        '''限制子类必须实现该抽象属性来按照DAP提取器来做类型转换
        DAP提取器
        函数            描述                                   SQL举例
        file            获取文件名，可指定分隔符                select file(name, 'u') nid from report
        dir             获取目录名，可指定分隔符                select dir(name, '.') name from report
        i64             字符串整数转换为64位整数                select i64(name) nid from (select file(name, 'u') name from report)
        f64             字符串浮点数转换为64位浮点数            select f64(name) nid from (select file(name, 'u') name from report)
        ts_h            时间戳字符串转换为小时时间片
                        可以指定多少小时为一片，如4小时时间片    select ts_h(time) h from t
        ts_m            时间戳字符串转换为分钟时间片
                        可以指定多少分钟为一片，如5分钟时间片    select ts_m(time) m from t
        ts_s            时间戳字符串转换为秒数时间片，可以指定多少秒为一片，如30秒时间片	select ts_s(time) s from t
        preg_grep       正则提取，提取指定匹配的元组            select preg_grep(name, '(\w+)(\d+)', 2) id from report
        i               标记字段值为64位整数                   select i(score) score from report
        f               标记字段值为64位浮点数                 select f(score) score from report
        s               标记字段值为字符串                     select s(name) name from report
        b               标记字段值为二进制                     select b(score) score from report
        '''
        pass


class IntegerExtractor(BaseFieldExtractor):
    def __init__(self, name):
        super(IntegerExtractor, self).__init__(name)

    @property
    def value(self):
        return 'i({0}) {0}'.format(self.name)


class FloatExtractor(BaseFieldExtractor):
    def __init__(self, name):
        super(FloatExtractor, self).__init__(name)

    @property
    def value(self):
        return 'f({0}) {0}'.format(self.name)


class StringExtractor(BaseFieldExtractor):
    def __init__(self, name):
        super(StringExtractor, self).__init__(name)

    @property
    def value(self):
        return 's({0}) {0}'.format(self.name)


class DatetimeExtractor(BaseFieldExtractor):
    def __init__(self, name):
        super(DatetimeExtractor, self).__init__(name)

    @property
    def value(self):
        return 's({0}) {0}'.format(self.name)
