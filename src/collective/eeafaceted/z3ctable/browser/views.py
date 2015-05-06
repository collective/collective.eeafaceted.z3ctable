# -*- coding: utf-8 -*-

from zope.i18n import translate
from zope.interface import implements
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

    # use class 'nosort' on table so Plone default CSS sorting is not applied
    cssClasses = {'table': 'listing nosort'}

    cssClassEven = u'odd'
    cssClassOdd = u'even'

    def __init__(self, context, request):
        ''' '''
        BrowserView.__init__(self, context, request)
        SequenceTable.__init__(self, context, request)
        self.criteria = ICriteria(self.context)

    def render_table(self, batch):
        self.setSortingCriteriaNameInRequest()
        self.update(batch)
        return self.render()

    def setSortingCriteriaNameInRequest(self):
        """Find the sorting criterion and store the name in the request so
           it can be accessed by the z3c.table."""
        for criterion in self.criteria.values():
            if criterion.widget == u'sorting':
                self.request.set('sorting_criterion_name', criterion.getId())
                return

    def _getViewFields(self):
        """Returns fields we want to show in the table."""
        colNames = ['Title', 'CreationDate', 'Creator', 'review_state', 'getText']
        # if we can get the collection we are working with,
        # use customViewFields defined on it if any
        for criterion in self.criteria.values():
            if criterion.widget in (u'collection-link', u'collection-radio'):
                # value is stored in the request with ending [], like 'c4[]'
                collectionUID = self.request.get('{0}[]'.format(criterion.getId()))
                catalog = getToolByName(self.context, 'portal_catalog')
                collection = catalog(UID=collectionUID)
                if collection:
                    collection = collection[0].getObject()
                    customViewFields = collection.getCustomViewFields()
                    if customViewFields:
                        colNames = customViewFields
        return colNames

    def _getColumnFor(self, colName):
        """This method returns column to use for given p_colName.
           This is made to manage specific usecase that are not , then call _autoColumnFor
           that will play it smart."""
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
                # that is column name + '__header_title'
                newColumn.header = translate(u'{0}__header_title'.format(colName),
                                             domain='collective.eeafaceted.z3ctable',
                                             context=self.request)
            if not newColumn.attrName:
                newColumn.attrName = colName
            columns.append(newColumn)
        return columns

    def sortRows(self):
        self.sortOn = self.update_sortOn()
        super(FacetedTableView, self).sortRows()

    def update_sortOn(self):
        sort_on_name = self.request.get('sorting_criterion_name', '')
        if sort_on_name:
            sort_on = self.request.form.get('%s[]' % sort_on_name, '')
            for c in self.columns:
                key = c.sort_index or c.attrName
                if key == sort_on:
                    return c.id
            return self.columns[0].id

    def getSortOrder(self):
        reverse = self.request.form.get('reversed[]', '')
        if reverse == 'on':
            return u'descending'
        return u'ascending'

    @property
    def values(self):
        return self.batch

    def update(self, batch):
        self.batch = batch
        super(FacetedTableView, self).update()
