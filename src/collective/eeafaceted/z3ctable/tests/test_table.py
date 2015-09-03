# -*- coding: utf-8 -*-

import lxml.html
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import ICriteria
from plone.batching import Batch


class TestTable(IntegrationTestCase):

    def test_Table_sortingCriterionName(self):
        """Test the _sortingCriterionName method that returns the __name__
           of the faceted 'sorting' criterion."""
        table = self.faceted_z3ctable_view
        # it is initialized together with the table and stored in table.sorting_criterion_name
        self.assertEquals(table._sortingCriterionName(), u'c2')
        self.assertEquals(table._sortingCriterionName(), table.sorting_criterion_name)
        # and it is actually the faceted sorting criterion
        self.assertEquals(ICriteria(table.context).get('c2').widget, u'sorting')
        # remove this widget, when no 'sorting' criterion found, entire sorting ability is disabled
        ICriteria(table.context).delete('c2')
        self.assertEquals(table._sortingCriterionName(), None)

    def test_Table_render_table(self):
        """Test the renderRow method that makes it possible for a single column
           to set CSS on the rendered row."""
        table = self.faceted_z3ctable_view
        # build a Batch and render the table
        brains = self.portal.portal_catalog(portal_type='Folder')
        # 1 brain
        self.assertEquals(len(brains), 1)
        batch = Batch(brains, size=5)
        rendered_table = lxml.html.fromstring(table.render_table(batch))
        # we have one table with 6 columns and 1 row
        # 1 row
        self.assertEquals(len(rendered_table.find('tbody').findall('tr')), 1)
        # 6 columns
        self.assertEquals(len(rendered_table.find('tbody').find('tr').findall('td')), 6)
        # the brain is actually displayed in the table
        brain = brains[0]
        self.assertEquals(rendered_table.find('tbody').find('tr').find('td').text_content(), brain.Title)
