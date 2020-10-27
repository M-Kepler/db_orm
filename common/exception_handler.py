# -*-coding:utf-8-*-

from .log import getLogger
from ..i18n.ui import gettext as _
from .exceptions import DapModelFieldsNotFound
from .exceptions import DapModelFilterNotFound
from .exceptions import DapQueryParamErr
from .exceptions import GetOriginalDataFailed


LOG = getLogger(__name__)
MODULE_NAME = "bbc.dc_tools.common.exception_handler"


class ExceptionHandler(object):
    @staticmethod
    def get_msg(ex, is_hide_detail=True):
        if isinstance(ex, DapModelFieldsNotFound):
            msg = _('%s$$dap_module_fields_not_found' % MODULE_NAME) % {
                "table": ex.table,
                "fields": ex.fields
            }
        elif isinstance(ex, DapModelFilterNotFound):
            msg = _('%s$$dap_module_filter_not_found' % MODULE_NAME) % {
                "filter": ex._filter
            }
        elif isinstance(ex, DapQueryParamErr):
            msg = _('%s$$dap_query_param_err' % MODULE_NAME)
        elif isinstance(ex, GetOriginalDataFailed):
            msg = _('%s$$get_original_date_failed' % MODULE_NAME)
        else:
            LOG.exception("exception_handler not handle error")
            if is_hide_detail:
                msg = _("common$$internal_server_error")
            else:
                msg = str(ex)

        return msg
