import os
import logging
from logging import CRITICAL, FATAL, ERROR, WARNING, WARN, INFO, DEBUG
from logging.handlers import SysLogHandler
from functools import wraps

from .const import Config


# note: CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET

ENV_MOD_NAME = 'LOG__MODULE_NAME'

FORMATTER = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]'
                              '[%(process)d][%(filename)s:%(lineno)d]  '
                              '%(message)s')

MODULE_FORMATTER = logging.Formatter('%(asctime)s %(name)s[%(process)d]: '
                                     '[%(process)d] %(filename)s:%(lineno)d '
                                     '%(message)s', '%b %d %H:%M:%S')


def get_level():
    try:
        # e.g.
        # [log]
        # level = debug

        level_map = {
            'critical': CRITICAL,
            'fatal':    FATAL,
            'error':    ERROR,
            'warn':     WARN,
            'info':     INFO,
            'debug':    DEBUG,
        }
        return level_map[Config.LOG_LEVEL]
    except Exception:
        return INFO


class ModuleLogger(logging.Logger):

    def __init__(self, name, level):
        self._cache_name = name
        self._cache_level = level
        self._inited = 0

    def _real_init(self):
        if self._inited:
            return
        current = os.environ.get(ENV_MOD_NAME)
        if current is None:
            current = ''
        else:
            current = 'app_' + current
        super(self.__class__, self).__init__(current, self._cache_level)

        try:
            sys_handler = SysLogHandler(facility=SysLogHandler.LOG_USER,
                                        address='/dev/log')
            sys_handler.setFormatter(MODULE_FORMATTER)
            self.addHandler(sys_handler)
        except Exception:
            pass
        else:
            self._inited = 1

    def debug(self, msg, *args, **kwargs):
        self._real_init()
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._real_init()
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._real_init()
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    warn = warning

    def error(self, msg, *args, **kwargs):
        self._real_init()
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._real_init()
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

    fatal = critical

    def trace_stack(self, func):

        @wraps(func)
        def trace_stack_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                self.exception('Unexpected error: ')
                raise
        return trace_stack_wrapper


def getLogger(name):
    return ModuleLogger(name, get_level())


def init(module_name):
    assert isinstance(module_name, (str, unicode)), \
            'Bad module_name: %s' % module_name

    current = os.environ.get(ENV_MOD_NAME)
    if current is not None:
        old_logger = getLogger(__name__)
        old_logger.error('Module log reinit to %s' % module_name)
    os.environ[ENV_MOD_NAME] = module_name
