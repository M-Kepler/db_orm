#-*-coding:utf-8-*-
''' bbc补丁包为了尽量不与原有代码产生冲突，减少合并工作量，所以国际化操作临时放在这里
'''

import os
import gettext
from ConfigParser import ConfigParser

CURR_PATH = os.path.abspath(os.path.curdir)


class _TransBase(object):
    def __init__(self, locale, lang, context):
        trans = gettext.translation(context, locale, languages=[lang])
        self.gettext = trans.gettext

    @staticmethod
    def get_trans_dir_path(locale, lang):
        return "%s/%s/LC_MESSAGES" % (locale, lang)

    @staticmethod
    def get_trans_file_path(locale, lang, context):
        return "%s/%s.po" % (_TransBase.get_trans_dir_path(locale,
                                                           lang), context)


class LocalCfg(object):
    LANG_SECTION = "locale"
    LOCAL_CFG_PATH = os.path.join(CURR_PATH,  "locale/locale.conf")
    LOCALE_DIR = os.path.join(CURR_PATH, "locale")

    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read(self.LOCAL_CFG_PATH)
        self.lang_section = self.LANG_SECTION

    @property
    def lang(self):
        return self.conf.get(self.lang_section, "lang")


class Trans(_TransBase):
    def __init__(self, context, lang=None):
        self.lang_conf = LocalCfg()
        lang = lang or self.lang_conf.lang
        super(self.__class__, self).__init__(
            self.lang_conf.LOCALE_DIR,
            lang,
            context
        )
