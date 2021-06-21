<!-- TOC -->

- [修订记录](#修订记录)
- [说明](#说明)
  - [测试](#测试)
- [DAP参考](#dap参考)
  - [DAP的一些说明](#dap的一些说明)
- [原有查询DAP的实现 `dc.py`](#原有查询dap的实现-dcpy)
- [`dc_orm` 使用说明](#dc_orm-使用说明)
  - [建表 `tables.py`](#建表-tablespy)
  - [查询](#查询)
- [`dc_orm` 实现说明](#dc_orm-实现说明)
  - [元类 `orm.py`](#元类-ormpy)
  - [字段抽象类 `fields.py`](#字段抽象类-fieldspy)
  - [聚合器抽象类 `combiners.py`](#聚合器抽象类-combinerspy)
  - [过滤器抽象类 `filters.py`](#过滤器抽象类-filterspy)
  - [提取器抽象类 `converter.py`](#提取器抽象类-converterpy)
  - [收集器抽象类 `collectors.py`](#收集器抽象类-collectorspy)
- [`TODO`](#todo)
- [使用 `DAP` 过程遇到的一些问题](#使用-dap-过程遇到的一些问题)
  - [功能不支持](#功能不支持)
  - [文档不全](#文档不全)

<!-- /TOC -->

# 修订记录

| 作者        | 时间     | 说明         |
| :---------- | :------- | :----------- |
| `huangjinjie` | `20200718` | 创建说明文档 |

# 说明

## 测试

- 在 BBC 环境上，把代码下载到 `home` 目录下，进入到 `~/dap_orm/test/` 执行 `test.sh` 即可

# DAP参考

> - [DAP文档](http://dap.pr.sangfor.org/index.php?s=/home/item/index)
> - [DAP使用指南](http://dap.pr.sangfor.org/index.php?s=/7&page_id=109)
> - [查询](http://dap.pr.sangfor.org/index.php?s=/7&page_id=106)
> - [SQL](http://dap.pr.sangfor.org/index.php?s=/2&page_id=70)
> - `联系人：`PR部门张斌、PR部门王振国

- `DAP` 数据计算与服务的平台，BBC上的告警、设备状态、信息上报等信息都存在DAP中，页面上的 `报表` 模块就是从DAP中取的数据

- 所有操作都可以通过向 `1087` 发 `POST` 请求来完成，包括建表和查询

- 调试sql是否正确的时候，可以通过DAP提供的 `mdd_sql.php` 来查询DAP中的数据记录，[开启方法参考本链接](http://code.sangfor.org/CN/BBC/Documents/bbc_business)

## DAP的一些说明

> - 为了避免`SQL`误用，默认不指定 `limit` 的情况下`SQL`引擎内部仍然会限制 `1000` 条的最终结果集
> - `select` 的字段不支持星号 `*`，而且如果字段名和SQL的保留字冲突，需要使用**反引号**表示，比如`foreign`和我们的无中生有列`@direction`。

# 原有查询DAP的实现 `dc.py`

- 原有查询DAP的操作封装在 `dc_tools/dc.py` 中了，但是目前该文件已经有 `2000+` 行，不方便做扩展

- 而且代码看上去不是很清晰，比如现在的需求 `DAP` 增加了一张表，如果沿用原有的接口，首先就要从这 `2000+` 行的代码文件中梳理出查询逻辑；而且里面糅合了很多业务逻辑在里面。

- 可能 `dc.py` 中是为了显示报表写的逻辑，目前的需求直接查表的话，就不沿用里面的 `Page` 元类了

- `BBC2.5.12版本` 中增加的查询 `qoe` 数据的接口，但是这部分代码基本是在拼 `sql`，与业务关联很大，无法基于此做扩展

# `dc_orm` 使用说明

> `BBC`上处理dap数据的代码放在 `dc_tools`模块；从名字完全猜不到 `dc_tools` 模块的用途，因为部门以前就叫 `dc`，后来才在代码中了解到 `dc = data center` 数据中心的意思

- `DAP` 使用起来和日常接触到的数据库有很多差异的地方，`dc_orm` 尽量把通用的操作封装起来，提供简单易用的接口供业务层去掉用，`SQL` 操作基本与 `sqlalchemy` 框架保持一致

## 建表 `tables.py`

```py
# -*-coding:utf-8-*-

'''
DAP 表模型
'''

from ..common.const import DapConfig
from ..orm.orm import Model
from ..orm.fields import IntegerField
from ..orm.fields import StringField


class BestExt(Model):
    '''
        数据经过 bbc后台服务 bp_app 后会根据数据上报的时间，按照日期分类，写入到磁盘中
        对于DAP，文件夹就是表，表就是文件夹

        - 第一个遇到的问题就是，这个表名是会变化的，日期不一样，查询的表也不一样
          所以表名用字符串来表示，查询的时候传入tb_date参数来对表名做格式化

        - DAP存储的原始数据都是经过URL编码的，要想获取原数据，需要指定DAP提供的提取器，
          dc_orm框架中，对表字段做了映射，每个字段都对应一个 Field 的子类，对字段的操作都
          可以在类里面完成，比如对数据类型做限制、增加默认值、构造DAP提取器等
        
        - __table__ 属性表示表的位置

        - __sort_by__ 在做分页查询的时候用到，如果不需要的话也可以不设置该属性
            属性指定默认的排序字段，可以指定多个字段，按照先后顺序排序
            就像SQL： `order by name, age` 中的 name, age
    '''
    # 指定查询Dap原始数据
    __table__ = DapConfig.BLOB_ORIGIN_DATA_ROOT.format("bestext")
    # 如：/sf/db/dap/log_data/store/bbc/blob/bestext/20200718

    # 指定查询Dap索引数据
    # __table__ = DapConfig.BLOB_INDEX_ROOT.format("bestext")
    # 如：/sf/db/dap/log_data/store/bbc/blob/table/bestext/20200718/bestext

    device_id = IntegerField(name="device_id", comment="设备ID")
    time = StringField(name="time", comment="记录上报时间")
    event_type = IntegerField(name="event_type", comment="事件类型")
    occur_time = IntegerField(name="occur_time", comment="线路劣化发生时间戳")
    link_id = StringField(name="link_id", comment="线路ID")
    link_status = StringField(name="link_status", comment="线路状态")
    detail = StringField(name="detail", comment="线路迁移具体信息")
    user_name = StringField(name="user_name", comment="线路连接的用户名")

    # 指定默认排序字段
    __sort_by__ = "occur_time"
    # __sort_by__ = "occur_time, link_id"
```

## 查询

> 单测文件 `test_orm.py` 包含了目前支持的所有sql操作，如需扩展，需要修改 `orm.py/Model` 模型类来支持

- **查询操作只会在调用 `all()、first()、asc()、desc()、offset()` 等少数几个函数的时候才会触发，目的是为了支持像 `sqlalchemy` 那样进行拼接 `sql`**

- 查询用法基本和 `sqlalchemy`保持一致，查询结果是表对象组成的列表，如果是 `first()` 则返回一个表对象

- `DAP` 提供了转换器、过滤器等来完成数据的过滤、转换等操作，所以实际构造 `sql`的语句和普通的 `sql` 有一定的差别；`dc_orm` 框架利用 `元类` 的特性，把这些操作都封装了起来，实际应用的时候不需要由开发人员自己取拼 `sql` 语句

- 查询 `DAP` 数据的方法是向 `DAP` 应用监听的 `1087`端口 发 `HTTP` 请求，[详细参数见此链接](http://dap.pr.sangfor.org/index.php?s=/7&page_id=106)

- 查询
  ```py
  # 指定查询某天的数据
  ret = BestExt.query(tb_data=20200718).all()
  # 指定某段日期
  ret = BestExt.query(start_date=20200710,
                      end_date=20200721).all()
  # 不指定日期，则查询全部该表的数据
  ret = BestExt.query().all()
  # 查询一条数据
  ret = BestExt.query().first()
  ```

- 过滤
  ```py
  where_args = [
      {
          "field": "event_type",
          "value": (1, 2),
          "filter": IncludeFilter
      }
  ]
  '''
  构建的查询语句是：
      where ('incude(event_type in %{event_type}s)')
  相对于SQL中的：
      where event_type in (1, 2)

  - 查询参数够着得有点奇葩，但也是无奈之举

  - DAP有一个叫过滤器的东西，需要对查询的字段做一番转换，构建这样的查询结构，可以校验查询的字段 field 是否存在

  - 对查询的值 value 做格式判断，比如对于IncludeFilter，值应该是tuple类型，filter表示过滤器

  '''
  ret = BestExt.query().filter(where=where_args).all()
  ```

- 限制条数
  ```py
  '''
      限制最终结果集的条数，DAP默认最多返回1000条记录
  '''
  limit_cnt = 100
  ret = BestExt.query().limit(limit=limit_cnt).all()
  ```

- 统计
  ```py
  ret = BestExt.query().count()
  ```

- 按字段求和
  ```py
  # 会对值检验是否属于表字段
  ret = BestExt.query().sum('device_id')
  ```

- 排序
  ```py
  # 会对值检验是否属于表字段
  ret = BestExt.query().order_by('occur_time').all()
  ```

- TODO 倒序查询
  ```py
  '''
      DAP 中的倒序查询操作很有限，只支持对特定数据的倒序
      DAP 中支持的写法：
      select i(device_id) from bestext limit -10  # 对查询出来的10条数据进行倒序
      这种 `limit -n ` 的做法还是不太妥，比如一次就查出 `n+2` 条数据，那最后那两条就无法保证是有序的了
      > 咨询过王振国，DAP确实没有像SQL那样的desc、asc的全表排序操作
      > 所以只能自己做扩展了...对查询回来的数据装到列表中，然后用sort函数做排序
  '''
  # FIXME 目前的实现是在order by 后面加 desc 或 asc
  # 这样拼接的SQL语句也可以查询回来，就是没有达到效果
  ret = BestExt.query().order_by('occur_time').desc()
  ret = BestExt.query().order_by('occur_time').asc()
  ```

- 组合查询
  > 和 `sqlalchemy` 一样，支持组合多个查询操作

  ```py
  ret = BestExt.query().limit(100).order_by('occur_time').all()
  ```

- **分页**
  > 分页在DAP中并不支持，本框架做法是查询出数据存放到redis中，然后通过lrange来取

  ```py
  curr_page = 10
  page_size = 20
  # TODO 验证一下数据正确性
  ret, total = BestExt.query().offset(curr_page=curr_page,
                                      page_size=page_size)
  ```

- `group by`
  ```py
  ret = self.BestExt.query().group_by('device_id', 'occur_time').all()
  ```

- 查询日期范围内的数据
  ```py
  ret = self.BestExt.query(start_date=20200711,
                           end_date=20200721).all()
  ```

# `dc_orm` 实现说明

> 直接看代码更详细

## 元类 `orm.py`

- `ModelMetacalss(type)` 元类
  - 重写 `type` 类的 `__new__` 方法，定义类的创建过程
  - 指定了由该元类实例化（元类实例化得到类、类实例化得到的就是对象了）出来的类（即本框架中的模型类）允许拥有的属性
  - 一些期望所有模型都有的属性，可以在元类中指明，比如定义基本的查询语句 `__select__`，类可以基于该语句上做扩展

- `Model(dict)` 模型类
  - 继承自 `dict` 类，字典的操作对该类同样适用
  - 指明由 `ModelMetaclass` 元类来实例化该类
  - 所有的 `sql` 语句都在该类中实现，比如 `where`、`group by`等，之所以
  - 所有的 `sql` 操作都定义为类方法，目的是为了支持拼接多个查询操作（定义为类方法，方法返回类本身，然后可以再调用其他的类方法），以及与 `sqlalchemy` 保持一致

## 字段抽象类 `fields.py`

```py
'''
表字段所映射的对象
Field子类可以扩展做字段验证、类型转换、设置默认值等
'''

from abc import ABCMeta, abstractproperty

from ..converters.extractors import IntegerConverter
from ..converters.extractors import StringConverter
from ..converters.extractors import DatetimeConverter


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
        return IntegerExtractor(self.name).value
```

## 聚合器抽象类 `combiners.py`

```py
# -*-coding:utf-8-*-
'''
查询聚合器
原SQL：
    select sum(device_id) from report
DAP SQL:
    select sum(device_id) device_ids from report

DAP文档:
    http://dap.pr.sangfor.org/index.php?s=/2&page_id=70
'''

from abc import ABCMeta, abstractproperty


class BaseCombiner(object):
    '''聚合器抽象基类
       定义了抽象属性filter，子类必须实现该方法
    '''

    __metaclass__ = ABCMeta

    def __init__(self, field=None):
        '''
        :param field 字段名
        '''
        self.field = field

    def __str__(self):
        return '<%s, %s>' % (self.__class__.__name__, self.field)

    @abstractproperty
    def combiner(self):
        '''DAP聚合器修饰后的查询
        DAP聚合器查询结果值不能与关键字同名（原始sql是可以的）
        比如 select sum(device_id) sum from 20200716 查询会报错
        '''
        pass


class SumCombiner(BaseCombiner):
    def __init__(self, field="%s"):
        '''
            查询聚合器也可以实例化的时候指定需要聚合的字段field，但是不建议这样做

            在orm.py的元类 ModelMateclass中，会构建一系列默认的SQL语句作为类属性
                cls_attrs['__sum__'] = cls_attrs['__base_sql__'] % SumCombiner().combiner
            实例化类的时候直接给这些属性传参就行了
                cls.__sum__.format(field)
            详见orm.py中的使用
        '''
        super(SumCombiner, self).__init__(field)

    @property
    def combiner(self):
        if self.field != "%s":
            return 'sum({0}) {0}s'.format(self.field)
        else:
            return 'sum({0}) {0}s'

```

## 过滤器抽象类 `filters.py`

```py
# -*-coding:utf-8-*-
'''
查询过滤器

原SQL：
    select dept from report where event_type in (1, 2) and device_id = 5;
DAP SQL:
    # where语句用and/or连接前要用加上括号，有需要的话要给字段套上过滤器
    select dept from report where (include(event_type) in (1, 2)) and (device_id = 5);

DAP文档:
    http://dap.pr.sangfor.org/index.php?s=/2&page_id=70
'''

from abc import ABCMeta, abstractproperty
from ..common.exceptions import DapModelFilterValueErr


class BaseFilter(object):
    '''过滤器抽象基类
       定义了抽象属性filter，子类必须实现该方法
    '''

    __metaclass__ = ABCMeta

    def __init__(self, field, value):
        '''
        :param field 字段名
        '''
        self.field = field
        self.value = value

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.field, self.value)

    @abstractproperty
    def filter(self):
        '''经过DAP提取器装饰后的字段'''
        pass


class IncludeFilter(BaseFilter):
    def __init__(self, field, value):
        super(IncludeFilter, self).__init__(field, value)

    @property
    def filter(self):
        if not isinstance(self.value, list):
            raise DapModelFilterValueErr(expect=tuple, got_value=type(self.value))
        return 'include(%s) in %s' % (self.field, str(tuple(self.value)))
```

## 提取器抽象类 `converter.py`

```py
# -*-coding:utf-8-*-
'''
字段提取器
DAP 存储的数据是经过URL编码的，要正常显示需要用提取器进行处理

- 原始sql:
    select event_type, occur_time from tb_name

- DAP的sql
    > 需要对字段套上提取器做解码才能正产显示值
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
        '''
        pass


class IntegerExtractor(BaseFieldExtractor):
    def __init__(self, name):
        super(IntegerExtractor, self).__init__(name)

    @property
    def value(self):
        return 'i({0}) {0}'.format(self.name)
```

## 收集器抽象类 `collectors.py`

```py
# -*-coding:utf-8-*-
'''
查询收集器
原SQL：
    select device_id from report where occur_date between (20200710, 20200713)
DAP SQL:
    select /* COLLECT:collector.date@core */ device_id from `/path/to/data/[0-9]*/kvd,20180101|20180103-20180409|20180106`

DAP文档:
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
    def __init__(self):
        super(DateCollector, self).__init__()

    @property
    def collector(self):
        return '/* COLLECT:collector.date@core */'
```

# `TODO`

- 目前实现的过滤器、聚合器等的种类比较少，仅满足当前的业务要求，如果后需要继续用 `dc_orm` 来处理存放在 `dap` 数据，需要开发人员自行在以上 `XXX器` 代码中做扩展

- 查询 `dap` 数据的方法是向 `指定` 端口发 `HTTP` 请求；如果后续扩展后表逐渐增多，查询操作很频繁，目前这种简单发 `HTTP` 请求的方式肯定是满足不了的

- 后续最好像 `db_service` 一样，做一个单独的服务，服务前端接受请求，后端调 `orm` 查询

- `子查询`

- `UNION查询`

# 使用 `DAP` 过程遇到的一些问题

## 功能不支持

- 不支持分页  
  DAP不支持分页，给出的理由是
  > 因为这不是一个很好的功能，每次翻页会导致重新查询，如果要查一个月，这个翻页代价比较大

- 不支持倒序、正序
  ```sql
  /* 不支持 asc desc的全表排序操作*/
  -- 正序
  select i(device_id) from bestext limit 100;
  -- 倒序
  select i(device_id) from bestext limit -100;
  ```

- 不支持查询全部的数据，但是通过 `mdd_sql.php` 可以  
  - `dap` 推荐使用向 `http://127.0.0.1:1087/call` 发 http 请求的方式来完成 `sql` 操作，但是这种方式如果不加 `limit` 参数，会默认限制只返回 `1000` 条数据
  - 但是通过 `http://10.119.110.11:1089/mdd_sql.php` 调试的时候发现，如果不加 `limit` 参数，是可以把数据全部查回来的（实测发现不受 1000 条的限制）.

- `count()` 聚合器的意义与原始 `sql` 有歧义
  - 原始 `sql`  
    ```sql
    select count(1) from report;
    select count(id) from report;
    -- 两个语句都表示表中有多少条数据

    -- 所有id值求和
    select sum(id) from report;
    ```
  - `DAP` 的 `sql`  
    ```sql
    -- 表示的是 `report` 表中所有的`device_id` 的总和
    -- 即 `sum` 的意思，但是 `dap` 已经有 `sum` 来支持计算统计了  
    select count(device_id) device_ids from report;
    -- 等价于
    select sum(device_id) device_ids from report;

    -- 表示的才是表中有多少条数据
    select count(1) from report;
    ```

## 文档不全  

- 文档不清晰  
  和 DAP 对接的时候，给了一份 `golang` 写的代码，但是并没有说明这份代码是干什么用的，只是让我们看一下这个例子。让我们误以为用 `dap` 建表必须用 `golang` 也写一份这样的代码才可以，谁知道，这份代码的目的其实也就是发 `POST` 请求。。。

- 在增加 `collectors.py` 收集器的过程中，也只是从DAP文档中看出查询日期区间需要加上`日期收集器`，没有具体的文档说明支持哪些收集器
