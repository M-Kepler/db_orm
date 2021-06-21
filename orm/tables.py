# -*-coding:utf-8-*-

'''
DAP 表模型
'''

from ..common.const import DapConfig
from ..orm.orm import Model
from ..orm.fields import IntegerField
from ..orm.fields import StringField


class BestExt(Model):
    """
    数据经过 bbc后台服务 bp_app 后会根据数据上报的时间，按照日期创建文件夹，并写入到磁盘中
    对于DAP，文件夹就是表，表就是文件夹

    - 第一个遇到的问题就是，这个表名是会变化的，日期不一样，查询的表也不一样
      所以表名用字符串来表示，查询的时候传入tb_date参数来对表名字符串做格式化

    - DAP存储的原始数据都是经过URL编码的，要想获取原数据，需要指定DAP提供的提取器，
      本框架中，对表字段做了映射，每个字段都对应一个 Field 的子类，对字段的操作都
      可以在类里面完成，比如对数据类型做限制、增加默认值、构造DAP提取器等

    - __table__ 属性表示表的位置

    - __sort_by__ 在做分页查询的时候会用到，如果不需要的话也可以不初始化该属性
        属性指定默认的排序字段，可以指定多个字段，按照先后顺序排序
        就像SQL： `order by name, age` 中的 name, age
    """

    # 指定查询Dap原始数据
    # __table__ = DapConfig.BLOB_ORIGIN_DATA_ROOT.format("bestext")
    # 如：/sf/db/dap/log_data/store/bbc/blob/bestext/20200718

    # 指定查询Dap索引数据
    __table__ = DapConfig.BLOB_INDEX_ROOT.format("bestext")
    # 如：/sf/db/dap/log_data/store/bbc/blob/table/bestext/20200718/bestext

    device_id = IntegerField(name="device_id", comment="设备ID")
    time = StringField(name="time", comment="记录上报时间")
    event_type = IntegerField(name="event_type", comment="事件类型")
    occur_time = IntegerField(name="occur_time", comment="线路劣化发生时间戳")
    update_time = IntegerField(name="update_time", comment="会话切换时间戳")
    link_id = StringField(name="link_id", comment="线路ID")
    link_status = StringField(name="link_status", comment="线路状态")
    detail = StringField(name="detail", comment="线路迁移具体信息")
    user_name = StringField(name="user_name", comment="线路连接的用户名")
    server_name = StringField(name="server_name", comment="线路连接的总部名称")

    # 指定默认排序字段
    __sort_by__ = "occur_time"
    # __sort_by__ = "occur_time, link_id"

    @classmethod
    def _format_dap_item(cls, dap_data):
        """
        查询dap时，如果指定 t_list 查询方式，则结果集只有字段内容，没有字段名
        orm.py 框架已经指定查询次序按字段排序，所以这里组装一下数据
        """
        return cls(**{
            "detail": dap_data[1],
            "device_id": dap_data[2],
            "event_type": dap_data[3],
            "link_id": dap_data[4],
            "link_status": dap_data[5],
            "occur_time": dap_data[6],
            "server_name": dap_data[7],
            "time": dap_data[8],
            "update_time": dap_data[9],
            "user_name": dap_data[10]
        })
