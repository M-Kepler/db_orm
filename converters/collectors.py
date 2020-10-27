# -*-coding:utf-8-*-
'''
查询收集器
原SQL：
    select device_id from report where occur_date between (20200710, 20200713)
DAP SQL:
    select /* COLLECT:collector.date@core */ device_id from `/path/to/data/[0-9]*/kvd,20180101|20180103-20180409|20180106`

DAP文档:
    没找到具体的文档，以下实现的日期收集器也只是从DAP文档的例子中看到的。。。
    咨询了王振国，也没给出文档位置，只是说查询的收集器用默认的就可以了
    http://dap.pr.sangfor.org/index.php?s=/2&page_id=70
'''

from abc import ABCMeta, abstractproperty


class BaseCollector(object):
    '''收集器抽象基类
       定义了抽象属性collector ，子类必须实现该方法
    '''

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def __str__(self):
        return '<%s>' % (self.__class__.__name__)

    @abstractproperty
    def collector(self, collector):
        pass


class DateCollector(BaseCollector):
    '''日期收集器
    '''
    def __init__(self):
        super(DateCollector, self).__init__()

    @property
    def collector(self):
        return '/* COLLECT:collector.date@core */'
