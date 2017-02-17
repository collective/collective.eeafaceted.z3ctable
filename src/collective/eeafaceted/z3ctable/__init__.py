# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.eeafaceted.z3ctable')

EMPTY_STRING = '__empty_string__'


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
