# -*-coding:utf-8-*-


class GlobalVariablesManager(object):
    """Get the global root. You can use 'g.xxx' to view
    some global variables.
    """
    query_cache = dict()


g = GlobalVariablesManager()
