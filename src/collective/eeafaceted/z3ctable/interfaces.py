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


class ITopAboveNavManager(IViewletManager):
    """A viewlet manager that sits at the top of the rendered table,
       above the batching navigation."""


class ITopBelowNavManager(IViewletManager):
    """A viewlet manager that sits at the top of the rendered table,
       below the batching navigation."""


class IBottomAboveNavManager(IViewletManager):
    """A viewlet manager that sits at the bottom of the rendered table,
       above the batching navigation."""


class IBottomBelowNavManager(IViewletManager):
    """A viewlet manager that sits at the bottom of the rendered table,
       below the batching navigation."""
