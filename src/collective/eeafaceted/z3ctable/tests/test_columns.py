# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.testing import IntegrationTestCase


class TestColumns(IntegrationTestCase):

    def test_default_columns_registration(self):
        """
        By default, the 5 following columns are registered for the
        eeafaceted.z3ctable listing:
        - Title;
        - Creation date;
        - Modification date;
        - Creator;
        - State;
        - Text.
        """
        self.faceted_z3ctable_view.initColumns()
        default_columns = set([col.__name__ for col in self.faceted_z3ctable_view.columns])
        self.assertEquals(default_columns, set(('Title',
                                               'Creator',
                                               'CreationDate',
                                               'ModificationDate',
                                               'review_state',
                                               'getText')))
