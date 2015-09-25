# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.viewlet.interfaces import IViewletManager
from plone.theme.interfaces import IDefaultPloneLayer

from z3c.table.interfaces import IColumn
from z3c.table.interfaces import ITable


class ICollectiveEeafacetedZ3ctableLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IFacetedTable(ITable):
    """ """


class IFacetedColumn(IColumn):
    """ """


class ITopManager(IViewletManager):
    """A viewlet manager that sits at the top of the rendered table
    """


class IBottomManager(IViewletManager):
    """A viewlet manager that sits at the bottom of the rendered table
    """
