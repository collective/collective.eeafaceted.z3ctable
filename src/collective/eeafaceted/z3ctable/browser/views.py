# encoding: utf-8

from Products.Five.browser import BrowserView
from collective.eeafaceted.z3ctable.interfaces import IFacetedTable
from collective.eeafaceted.z3ctable.browser.columns import AuthorColumn
from collective.eeafaceted.z3ctable.browser.columns import StateColumn
from collective.eeafaceted.z3ctable.browser.columns import TitleColumn
from z3c.table.table import SequenceTable
from zope.interface import implements


class FacetedTableView(BrowserView):

    def render_table(self, batch):
        self.setSortingCriteriaNameInRequest()
        table = FacetedTable(self.context, self.request)
        table.update(batch)
        return table.render()

    def setSortingCriteriaNameInRequest(self):
        """Find the sorting criterion and store the name in the request so
           it can be accessed by the z3c.table."""
        config = self.context.restrictedTraverse('@@configure_faceted.html')
        for criterion in config.get_criteria():
            if criterion.widget == u'sorting':
                self.request.set('sorting_criterion_name', criterion.__name__)
                return


class FacetedTable(SequenceTable):
    implements(IFacetedTable)

    # use class 'nosort' on table so Plone default CSS sorting is not applied
    cssClasses = {'table': 'listing nosort'}

    cssClassEven = u'odd'
    cssClassOdd = u'even'
    sortOn = 'table-number-0'

    def setUpColumns(self):
        columns = []
        titleColumn = TitleColumn(self.context, self.request, self)
        titleColumn.weight = 1
        columns.append(titleColumn)
        authorColumn = AuthorColumn(self.context, self.request, self)
        authorColumn.weight = 1
        columns.append(authorColumn)
        stateColumn = StateColumn(self.context, self.request, self)
        stateColumn.weight = 1
        columns.append(stateColumn)
        return columns

    def sortRows(self):
        self.sortOn = self.update_sortOn()
        super(FacetedTable, self).sortRows()

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
        return [brain for brain in self.batch]

    def update(self, batch):
        self.batch = batch
        super(FacetedTable, self).update()
