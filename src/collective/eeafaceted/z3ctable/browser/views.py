# -*- coding: utf-8 -*-

from zope.component import queryMultiAdapter
from zope.interface import implements
from z3c.table import interfaces
from z3c.table.table import SequenceTable
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from eea.facetednavigation.interfaces import ICriteria
from collective.eeafaceted.z3ctable.interfaces import IFacetedTable
from collective.eeafaceted.z3ctable.columns import AwakeObjectMethodColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import I18nColumn
from collective.eeafaceted.z3ctable.columns import TitleColumn


class FacetedTableView(BrowserView, SequenceTable):

    implements(IFacetedTable)

    cssClassEven = u'odd'
    cssClassOdd = u'even'
    cssClasses = {'table': 'faceted-table-results listing nosort'}

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        SequenceTable.__init__(self, context, request)
        self.criteria = ICriteria(self.context)
        view = queryMultiAdapter((self.context, self.request), name=u'faceted_query')
        self.query = view.criteria()
        self.sorting_criterion_name = self._sortingCriterionName()
        # convenience
        self.portal_url = getToolByName(self.context, 'portal_url').getPortalObject().absolute_url()

    def render_table(self, batch):
        self.update(batch)
        return self.render()

    def _sortingCriterionName(self):
        """Find the sorting criterion and store the name in the request so
           it can be accessed by the z3c.table."""
        for criterion in self.criteria.values():
            if criterion.widget == u'sorting':
                return criterion.getId()

    def _getViewFields(self):
        """Returns fields we want to show in the table."""
        colNames = ['Title', 'CreationDate', 'Creator', 'review_state', 'getText']
        return colNames

    def _getColumnFor(self, colName):
        """This method returns column to use for given p_colName.
           This will :
           - call _manualColumn;
           - call _autoColumnFor."""
        column = self._manualColumnFor(colName)
        if not column:
            column = self._autoColumnFor(colName)
        return column

    def _manualColumnFor(self, colName):
        """This method will get the column to use for given p_colName.
           This is made to manage columns not linked to an index, so not
           managed automatically by self._autoColumnFor."""
        # special column for Title
        if colName == 'Title':
            return TitleColumn(self.context, self.request, self)
        # special column for Creator
        elif colName == 'Creator':
            return MemberIdColumn(self.context, self.request, self)
        elif colName in ('CreationDate', 'ModificationDate', 'EffectiveDate', 'ExpirationDate'):
            # CreationDate and ModificationDate are handled manually
            # because index is created and modified...
            column = DateColumn(self.context, self.request, self)
            # Index is not the same as metadata... we have to map values
            mapping = {'CreationDate': 'created',
                       'ModificationDate': 'modified',
                       'EffectiveDate': 'effective',
                       'ExpirationDate': 'expired',
                       }
            column.sort_index = mapping[colName]
            return column
        elif colName == 'getText':
            return AwakeObjectMethodColumn(self.context, self.request, self)

    def _autoColumnFor(self, colName):
        """This method will automatically get the relevant column to use for given p_colName."""
        # for other columns, try to get the corresponding index type
        # in the portal_catalog and use relevant column type
        catalog = getToolByName(self.context, 'portal_catalog')
        if colName in catalog.indexes():
            indexType = catalog.Indexes[colName].getTagName()
            if indexType == 'DateIndex':
                return DateColumn(self.context, self.request, self)
            elif indexType == 'ZCTextIndex':
                return BaseColumn(self.context, self.request, self)
        # in other cases, try to translate content
        return I18nColumn(self.context, self.request, self)

    def setUpColumns(self):
        # show some default columns
        colNames = self._getViewFields()
        columns = []
        for colName in colNames:
            newColumn = self._getColumnFor(colName)
            if not newColumn:
                raise KeyError('No column could be found for "{0}"'.format(colName))
            if not newColumn.header:
                # the column header is translated, we build a msgid
                # that is 'header_' + column name
                newColumn.header = u'header_{0}'.format(colName)
            if not newColumn.attrName:
                newColumn.attrName = colName
            columns.append(newColumn)
        return columns

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
        return u'\n    <tr%s>%s\n    </tr>' % (cssClass, u''.join(cells))

    def renderCell(self, item, column, colspan=0):
        """Override to be call getCSSClasses on column, no cssClasses."""
        if interfaces.INoneCell.providedBy(column):
            return u''
        # XXX begin adaptation by collective.eeafaceted.z3ctable
        #cssClass = column.cssClasses.get('td')
        cssClass = column.getCSSClasses(item).get('td', None)
        # XXX end adaptation by collective.eeafaceted.z3ctable
        cssClass = self.getCSSHighlightClass(column, item, cssClass)
        cssClass = self.getCSSSortClass(column, cssClass)
        cssClass = self.getCSSClass('td', cssClass)
        colspanStr = colspan and ' colspan="%s"' % colspan or ''
        return u'\n      <td%s%s>%s</td>' % (cssClass,
                                             colspanStr,
                                             column.renderCell(item))

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
