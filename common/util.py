# coding=utf-8
import time
import json
import datetime
import urllib
import uuid

from tempfile import NamedTemporaryFile

from logging import getLogger

LOG = getLogger(__name__)


def unique_id():
    """
    生成一个任意的ID，用作查询时候的query_id。
    :return: 随机生成的ID。
    """

    return str(uuid.uuid4())


def today():
    """
    返回今天的日期字符串，YYYYmmdd的形式。
    :return: 今天的日期，以字符串形式。
    """
    return datetime.date.today().strftime('%Y%m%d')


def yesterday():
    """
    返回昨天的日期字符串，YYYYmmdd的形式。
    :return: 今天的日期，以字符串形式。
    """
    return (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')


def yesterday_nowtime():
    """
    返回24小时之前的时间戳
    :return: 24小时之前的时间戳
    """
    return int(time.time()) - 3600 * 24


def convert_date_fmt_dc(d):
    """
    将日期格式转换为能为DAP所用。
    :param d: 日期。
    :return: 转换后的结果，字符串形式。
    """
    return datetime.datetime.strptime(d, '%Y-%m-%d').strftime('%Y%m%d')


def url_json_decode(raw_data):
    """
    对原生数据进行url解码后再进行Json反序列化.
    :param raw_data: 原始查询结果.
    :return: 解码后的数据.
    """
    if isinstance(raw_data, unicode):
        raw_data = raw_data.encode('utf-8')
    try:
        data = json.loads(urllib.unquote(raw_data), strict=False)
    except ValueError as e:
        LOG.error('raw data decode error : %s' % str(e))
        return [], None

    return data.get('data', []), data.get('total')


def minutes_before_now(n=10):
    """
    返回若干分钟之前的时间戳
    :param n: 分钟数
    :return: 时间戳
    """
    return int(time.time()) - n*60


def walk_date(start, end):
    """
    对start_date到end_date之间的日期进行遍历,返回便利结果所组成的list
    :param start: 起始日期
    :param end: 终止日期
    :return: 日期列表
    """

    if int(start) > int(end):
        raise ValueError('start date must early than end date')

    # 将start那一天的日期加入res，然后向后推一天
    res = [start]

    while start != end:
        d = datetime.datetime.strptime(start, '%Y%m%d')
        start = (d + datetime.timedelta(days=1)).strftime('%Y%m%d')
        res.append(start)

    return res


def write_temp_file(content):
    """
    由系统随机生成一个文件（文件名不会和已有文件重复），写入指定内容到文件中，返回文件名。
    :param content: 文件内容。
    :return: 随机生成的文件名。
    """
    with NamedTemporaryFile('w+', delete=False) as f:
        f.write(content)
        LOG.debug('dap param file content : %s' % str(content))
        return f.name
