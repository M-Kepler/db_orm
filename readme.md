<!-- TOC -->

- [修订记录](#修订记录)
- [说明](#说明)
  - [测试](#测试)
  - [建表](#建表)
  - [查询](#查询)
- [实现说明](#实现说明)
  - [元类 `orm.py`](#元类-ormpy)
- [`TODO`](#todo)

<!-- /TOC -->

# 修订记录

| 作者        | 时间     | 说明         |
| :---------- | :------- | :----------- |
| `huangjinjie` | `20200718` | 创建说明文档 |

# 说明

> 单测文件 `test_orm.py` 包含了目前支持的所有sql操作，如需扩展，需要修改 `orm.py/Model` 模型类来支持

## 测试

- 环境上，把代码下载到 `home` 目录下，进入到 `~/db_orm/test/` 执行 `test.sh` 即可

## 建表

> `tables.py`

## 查询

- **查询操作只会在调用 `all()、first()、asc()、desc()、offset()` 等少数几个函数的时候才会触发，目的是为了支持像 `sqlalchemy` 那样进行拼接 `sql`**

- 查询用法基本和 `sqlalchemy`保持一致，查询结果是表对象组成的列表，如果是 `first()` 则返回一个表对象

- `DB` 提供了转换器、过滤器等来完成数据的过滤、转换等操作，所以实际构造 `sql`的语句和普通的 `sql` 有一定的差别；`dc_orm` 框架利用 `元类` 的特性，把这些操作都封装了起来，实际应用的时候不需要由开发人员自己取拼 `sql` 语句

- 查询 `DB` 数据的方法是向 `DB` 应用监听的 `1087`端口 发 ` 

- 查询
  ```py
  # 指定查询某天的数据
  ret = test_tb.query(tb_data=20200718).all()
  # 指定某段日期
  ret = test_tb.query(start_date=20200710,
                      end_date=20200721).all()
  # 不指定日期，则查询全部该表的数据
  ret = test_tb.query().all()
  # 查询一条数据
  ret = test_tb.query().first()
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
  """
  构建的查询语句是：
      where ('incude(event_type in %{event_type}s)')
  相对于SQL中的：
      where event_type in (1, 2)

  - 查询参数够着得有点奇葩，但也是无奈之举

  - DB有一个叫过滤器的东西，需要对查询的字段做一番转换，构建这样的查询结构，可以校验查询的字段 field 是否存在

  - 对查询的值 value 做格式判断，比如对于IncludeFilter，值应该是tuple类型，filter表示过滤器

  """
  ret = test_tb.query().filter(where=where_args).all()
  ```

- 限制条数
  ```py
  """
  限制最终结果集的条数，DB默认最多返回1000条记录
  """
  limit_cnt = 100
  ret = test_tb.query().limit(limit=limit_cnt).all()
  ```

- 统计
  ```py
  ret = test_tb.query().count()
  ```

- 按字段求和
  ```py
  # 会对值检验是否属于表字段
  ret = test_tb.query().sum('device_id')
  ```

- 排序
  ```py
  # 会对值检验是否属于表字段
  ret = test_tb.query().order_by('occur_time').all()
  ```

- TODO 倒序查询
  ```py
  """
  DB 中的倒序查询操作很有限，只支持对特定数据的倒序

  DB 中支持的写法：
  select i(device_id) from test_tb limit -10  # 对查询出来的10条数据进行倒序
  这种 `limit -n ` 的做法还是不太妥，比如一次就查出 `n+2` 条数据，那最后那两条就无法保证是有序的了
  > 咨询过王振国，DB确实没有像SQL那样的desc、asc的全表排序操作
  > 所以只能自己做扩展了...对查询回来的数据装到列表中，然后用sort函数做排序
  """
  # FIXME 目前的实现是在order by 后面加 desc 或 asc
  # 这样拼接的SQL语句也可以查询回来，就是没有达到效果
  ret = test_tb.query().order_by('occur_time').desc()
  ret = test_tb.query().order_by('occur_time').asc()
  ```

- 组合查询
  > 和 `sqlalchemy` 一样，支持组合多个查询操作

  ```py
  ret = test_tb.query().limit(100).order_by('occur_time').all()
  ```

- 分页

  > 分页在DB中并不支持，本框架做法是查询出数据存放到redis中，然后通过lrange来取

  ```py
  curr_page = 10
  page_size = 20
  ret, total = test_tb.query().offset(curr_page=curr_page,
                                      page_size=page_size)
  ```

- `group by`
  ```py
  ret = self.test_tb.query().group_by('device_id', 'occur_time').all()
  ```

- 查询日期范围内的数据
  ```py
  ret = self.test_tb.query(start_date=20200711,
                           end_date=20200721).all()
  ```

# 实现说明

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

# `TODO`

- 目前实现的过滤器、聚合器等的种类比较少，仅满足当前的业务要求，如果后需要继续用 `dc_orm` 来处理存放在 `db` 数据，需要开发人员自行在以上 `XXX器` 代码中做扩展

- 查询 `db` 数据的方法是向 `指定` 端口发 ` 

- 后续可以做成一个单独的服务，服务前端接受请求，后端调 `orm` 查询

- `子查询`

- `UNION查询`
