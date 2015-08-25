# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.columns import AwakeObjectMethodColumn
from collective.eeafaceted.z3ctable.columns import CreationDateColumn
from collective.eeafaceted.z3ctable.columns import I18nColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import TitleColumn
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase


class TestColumns(IntegrationTestCase):

    def test_default_columns_registration(self):
        """
        By default, the 5 following columns are registered for the
        eeafaceted.z3ctable listing:
        - Title
        - Creation date
        - Creator
        - State
        - Text
        """
        self.faceted_z3ctable_view.initColumns()
        default_columns = self.faceted_z3ctable_view.columns

        msg = 'Expected the first column to be a TitleColumn'
        self.assertTrue(isinstance(default_columns[0], TitleColumn), msg=msg)

        msg = 'Expected the second column to be a CreationDateColumn'
        self.assertTrue(isinstance(default_columns[1], CreationDateColumn), msg=msg)

        msg = 'Expected the third column to be a MemberIdColumn'
        self.assertTrue(isinstance(default_columns[2], MemberIdColumn), msg=msg)

        msg = 'Expected the fourth column to be a I18nColumn'
        self.assertTrue(isinstance(default_columns[3], I18nColumn), msg=msg)

        msg = 'Expected the fifth column to be a AwakeObjectMethodColumn'
        self.assertTrue(isinstance(default_columns[4], AwakeObjectMethodColumn), msg=msg)
