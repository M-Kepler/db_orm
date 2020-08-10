# -*-coding:utf-8-*-

class GetOriginalDataFailed(Exception):
    pass


class DapModelFieldsNotFound(Exception):
    def __init__(self, table, fields):
        self.table = table
        self.fields = fields


class DapModelFilterNotFound(Exception):
    def __init__(self, _filter):
        self.filter = _filter


class DapQueryParamErr(Exception):
    pass


class DapModelFilterValueErr(Exception):
    def __init__(self, expect, got_value):
        self.expect = expect
        self.got_value = got_value
