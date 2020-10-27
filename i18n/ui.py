# -*-coding:utf-8-*-
#!/usr/bin/env python

from .i18n import Trans

_cache_trans = None


def gettext(*args, **kwargs):
    global _cache_trans
    if not _cache_trans:
        _cache_trans = Trans('ui')
    return _cache_trans.gettext(*args, **kwargs)


if __name__ == "__main__":
    print(
        gettext(
            "bbc.manage.sp_upgrade.exception_handler$$sp_upgrade_config_save_error"
        ))
