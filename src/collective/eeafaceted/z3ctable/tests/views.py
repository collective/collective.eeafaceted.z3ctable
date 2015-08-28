# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView

CALL_RESULT = 'Browser view call result'


class TestingBrowserCallView(BrowserView):

    def index(self):
        """ """
        return CALL_RESULT
