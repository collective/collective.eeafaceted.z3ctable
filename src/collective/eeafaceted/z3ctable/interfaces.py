# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from plone.theme.interfaces import IDefaultPloneLayer

from z3c.table.interfaces import IColumn
from z3c.table.interfaces import ITable


class ICollectiveEeafacetedZ3ctableLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IFacetedTable(ITable):
    """ """


class IFacetedColumn(IColumn):
    """ """
