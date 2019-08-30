from zope.publisher.browser import BrowserView
from zope.i18n import translate as _

TEMPLATE = """\
var no_selected_items = "%(no_selected_items)s";
"""


class JSVariables(BrowserView):

    def __call__(self, *args, **kwargs):
        response = self.request.response
        response.setHeader('content-type', 'text/javascript;;charset=utf-8')

        no_selected_items = _('no_selected_items',
                              default="Please select at least one element.",
                              domain='collective.eeafaceted.z3ctable',
                              context=self.request)
        return TEMPLATE % dict(
            no_selected_items=no_selected_items,
        )
