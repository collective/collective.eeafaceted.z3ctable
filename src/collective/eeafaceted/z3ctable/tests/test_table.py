# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import ICriteria
from plone.batching import Batch

import lxml.html


class TestTable(IntegrationTestCase):

    def test_Table_sortingCriterionName(self):
        """Test the _sortingCriterionName method that returns the __name__
           of the faceted 'sorting' criterion."""
        table = self.faceted_z3ctable_view
        # it is initialized together with the table and stored in table.sorting_criterion_name
        self.assertEqual(table._sortingCriterionName(), u'c2')
        self.assertEqual(table._sortingCriterionName(), table.sorting_criterion_name)
        # and it is actually the faceted sorting criterion
        self.assertEqual(ICriteria(table.context).get('c2').widget, u'sorting')
        # remove this widget, when no 'sorting' criterion found, entire sorting ability is disabled
        ICriteria(table.context).delete('c2')
        self.assertEqual(table._sortingCriterionName(), None)

    def test_Table_render_table(self):
        """Test the renderRow method that makes it possible for a single column
           to set CSS on the rendered row."""
        table = self.faceted_z3ctable_view
        # build a Batch and render the table
        brains = self.portal.portal_catalog(portal_type='Folder')
        # 1 brain
        self.assertEqual(len(brains), 1)
        batch = Batch(brains, size=5)
        rendered_table = lxml.html.fromstring(table.render_table(batch))
        # we have one table with 7 columns and 1 row
        # 1 row
        self.assertEqual(len(rendered_table.find('tbody').findall('tr')), 1)
        # 9 columns
        self.assertEqual(len(rendered_table.find('tbody').find('tr').findall('td')), 9)
        # the brain is actually displayed in the table
        brain = brains[0]
        self.assertEqual(rendered_table.find('tbody').find('tr').find('td').text_content(), brain.Title)

    def test_Table_CSS_on_tr_from_cell(self):
        """table.renderRow was overrided to take into account 'tr' CSS classes defined on a column."""
        table = self.faceted_z3ctable_view
        column = BaseColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = 'Title'
        table.nameColumn(column, 'Title')
        # build a Batch
        brains = self.portal.portal_catalog(portal_type='Folder')
        batch = Batch(brains, size=5)
        # adapt css defined for column to change <tr> applied CSS
        column.getCSSClasses = lambda x: {'tr': 'special_tr_class'}
        # ok, now make table.setUpColumns take our configured column
        self.portal.REQUEST.set('column', column)
        table.setUpColumns = lambda *x: [__import__('zope').component.hooks.getSite().REQUEST.get('column'), ]
        rendered_table = lxml.html.fromstring(table.render_table(batch))
        # the class is applied to the <tr>, in addition to the 'odd' class
        self.assertEqual(rendered_table.find('tbody').find('tr').attrib['class'], 'odd special_tr_class')

    def test_columns_ordering(self):
        """table.orderColumns take the ignoreColumnWeight parameter into account
        to keep columns as ordered by setUpColumns or to order them by weight."""
        table = self.faceted_z3ctable_view

        # when ignoreColumnWeight is set to True, colums are kept ordered
        # as found on setUpColumns
        table.ignoreColumnWeight = True
        table.initColumns()

        columns = [col.__name__ for col in table.columns]
        self.assertEqual(columns, table._getViewFields())

        weights = [col.__class__.weight for col in table.columns]
        ordered_weights = sorted(weights)
        self.assertNotEquals(weights, ordered_weights)

        # when ignoreColumnWeight is set to False, colums are kept ordered
        # by weight on each column
        table.ignoreColumnWeight = False
        table.initColumns()

        columns = [col.__name__ for col in table.columns]
        self.assertNotEquals(columns, table._getViewFields())

        weights = [col.__class__.weight for col in table.columns]
        ordered_weights = sorted(weights)
        self.assertEqual(weights, ordered_weights)
