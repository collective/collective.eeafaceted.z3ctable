# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.interfaces import IFacetedTable
from datetime import datetime
from datetime import timedelta
from eea.facetednavigation.interfaces import ICriteria
from plone import api
from Products.Five.browser import BrowserView
from z3c.table.interfaces import IColumn
from z3c.table.interfaces import INoneCell
from z3c.table.table import SequenceTable
from zope.component import getAdapters
from zope.component import queryMultiAdapter
from zope.interface import implements

import logging
import traceback


logger = logging.getLogger('collective.eeafaceted.z3ctable')


class ExtendedCSSTable(SequenceTable):
    """SequenceTable that manage ability to set CSS per cell and
       depending on cell value."""

    table_id = ''
    row_id_prefix = ''

    def renderTable(self):
        self.debug = bool(self.request.form.get('debug[]', False))
        rendered_table = super(ExtendedCSSTable, self).renderTable()
        if rendered_table and self.table_id:
            # include 'id' when 'class' defined
            rendered_table = rendered_table.replace('<table ', '<table id="%s" ' % self.table_id, 1)
            # include 'id' when <table>
            rendered_table = rendered_table.replace('<table>', '<table id="%s">' % self.table_id, 1)
        return rendered_table

    def renderRow(self, row, cssClass=None):
        """Override to be able to apply a class on the TR defined on a column,
           because by default, the only way to define a class for the TR
           is on the table, and we need to do it from the column..."""
        isSelected = self.isSelectedRow(row)
        if isSelected and self.cssClassSelected and cssClass:
            cssClass = '%s %s' % (self.cssClassSelected, cssClass)
        elif isSelected and self.cssClassSelected:
            cssClass = self.cssClassSelected
        # XXX begin adaptation by collective.eeafaceted.z3ctable
        # get a getCSSClasses method on each column to see if something
        # is defined for the TR
        trCSSClasses = [cssClass, ]
        for item, column, index in row:
            trCSSClass = column.getCSSClasses(item).get('tr', None)
            if trCSSClass:
                trCSSClasses.append(trCSSClass)
        cssClasses = ' '.join(trCSSClasses)
        cssClass = self.getCSSClass('tr', cssClasses)
        # XXX end adaptation by collective.eeafaceted.z3ctable
        cells = [self.renderCell(item, col, colspan)
                 for item, col, colspan in row]
        if self.row_id_prefix:
            return u'\n    <tr id="%s%s" %s>%s\n    </tr>' % (
                self.row_id_prefix, item.UID, cssClass, u''.join(cells))
        else:
            return u'\n    <tr %s>%s\n    </tr>' % (
                cssClass, u''.join(cells))

    def renderCell(self, item, column, colspan=0):
        """Override to be call getCSSClasses on column, no cssClasses."""
        if INoneCell.providedBy(column):
            return u''
        # XXX begin adaptation by collective.eeafaceted.z3ctable
        # cssClass = column.cssClasses.get('td')
        cssClass = column.getCSSClasses(item).get('td', None)
        # XXX end adaptation by collective.eeafaceted.z3ctable
        cssClass = self.getCSSHighlightClass(column, item, cssClass)
        cssClass = self.getCSSSortClass(column, cssClass)
        cssClass = self.getCSSClass('td', cssClass)
        colspanStr = colspan and ' colspan="%s"' % colspan or ''
        start = datetime.now()
        renderedCell = column.renderCell(item)
        if self.debug:
            if not hasattr(column, 'cumulative_time'):
                column.cumulative_time = timedelta(0)
            end = datetime.now()
            difference = end - start
            column.cumulative_time += difference
            # not last row?
            if item.UID != self.batch[self.batch.length - 1].UID:
                renderedCell = u'\n      <td%s%s>%s<br>%f</td>' % (
                    cssClass, colspanStr, renderedCell,
                    difference.total_seconds())
            else:
                if column != self.columns[-1]:
                    renderedCell = u'\n      <td%s%s>%s<br>%f<br><strong>%f</strong></td>' % (
                        cssClass, colspanStr, renderedCell,
                        difference.total_seconds(), column.cumulative_time.total_seconds())
                else:
                    total_time = sum([col.cumulative_time for col in self.columns], timedelta(0))
                    renderedCell = u'\n      <td%s%s>%s<br>%f<br><strong>%f<br>Total: %f</strong></td>' % (
                        cssClass, colspanStr, renderedCell,
                        difference.total_seconds(),
                        column.cumulative_time.total_seconds(),
                        total_time.total_seconds())
        else:
            renderedCell = u'\n      <td%s%s>%s</td>' % (
                cssClass, colspanStr, renderedCell)
        return renderedCell


class FacetedTableView(BrowserView, ExtendedCSSTable):

    implements(IFacetedTable)

    # workaround so z3c.table does not manage batching
    startBatchingAt = 9999
    cssClassEven = u'odd'
    cssClassOdd = u'even'
    cssClasses = {'table': 'faceted-table-results listing nosort'}
    ignoreColumnWeight = False  # when set to True, keep columns ordered as returned by '_getViewFields'
    table_id = 'faceted_table'
    row_id_prefix = 'row_'

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        SequenceTable.__init__(self, context, request)
        self.criteria = ICriteria(self.context)
        view = queryMultiAdapter((self.context, self.request), name=u'faceted_query')
        self.query = view.criteria()
        self.sorting_criterion_name = self._sortingCriterionName()
        # convenience
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url()

    def render_table(self, batch):
        self.update(batch)
        try:
            return self.render()
        except Exception, exc:
            # in case an error occured, catch it or it freezes the web page
            # because faceted JS disable page and error raised does not unlock
            traceback.print_exc(None)
            logger.error(exc)
            return "An error occured (%s %s), this should not happen, " \
                "try to go back to the home page." % \
                (exc.__class__.__name__, exc.message)

    def _sortingCriterionName(self):
        """Find the sorting criterion and store the name in the request so
           it can be accessed by the z3c.table."""
        for criterion in self.criteria.values():
            if criterion.widget == u'sorting':
                return criterion.getId()

    def _getViewFields(self):
        """Returns fields we want to show in the table."""
        col_names = [col[0] for col in getAdapters((self.context, self.request, self), IColumn)]
        return col_names

    def setUpColumns(self):
        # show some default columns
        col_names = self._getViewFields()
        cols = []
        for name in col_names:
            column = queryMultiAdapter(
                (self.context, self.request, self),
                interface=IColumn,
                name=name
            )
            cols.append(self.nameColumn(column, name))

        return cols

    def nameColumn(self, column, name):
        column.__name__ = name

        if not column.header:
            # the column header is translated, we build a msgid
            # that is 'header_' + column name
            column.header = u'header_{0}'.format(name)

        if not column.attrName:
            column.attrName = name

        return column

    def orderColumns(self):
        """ Order columns of the table."""

        if self.ignoreColumnWeight:
            for i, column in enumerate(self.columns):
                column.weight = i

        super(FacetedTableView, self).orderColumns()

    def sortRows(self):
        """Rows are sorted by the catalog query, do not let z3c.table sort rows."""
        return

    def getSortOrder(self):
        return self.query.get('sort_order', 'ascending')

    @property
    def values(self):
        return self.batch

    def update(self, batch):
        self.batch = batch
        super(FacetedTableView, self).update()

    def getBatchSize(self):
        return self.batch.length
