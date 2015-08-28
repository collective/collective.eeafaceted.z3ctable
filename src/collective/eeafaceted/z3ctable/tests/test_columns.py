# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.columns import AwakeObjectGetAttrColumn
from collective.eeafaceted.z3ctable.columns import AwakeObjectMethodColumn
from collective.eeafaceted.z3ctable.columns import BrowserViewCallColumn
from collective.eeafaceted.z3ctable.columns import CheckBoxColumn
from collective.eeafaceted.z3ctable.columns import ColorColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import I18nColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.eeafaceted.z3ctable.tests.views import CALL_RESULT


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

    def test_AwakeObjectGetAttrColumn(self):
        """This will wake the given catalog brain and getattr the attrName on it.
           This is used when displaying in a column an attribute that is not a catalog metadata."""
        table = self.faceted_z3ctable_view
        column = AwakeObjectGetAttrColumn(self.portal, self.portal.REQUEST, table)
        # we will use the 'eea_faceted' folder as a brain
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if column.attrName is not an attribute, it will return u''
        column.attrName = 'someUnexistingAttribute'
        self.assertEquals(column.renderCell(brain), u'-')
        # now an existing attribute
        column.attrName = '_at_uid'
        self.assertEquals(column.renderCell(brain), self.eea_folder._at_uid)

    def test_AwakeObjectMethodColumn(self):
        """This will wake the given catalog brain and call the attrName on it.
           This is used when displaying in a column a method result that is not a catalog metadata."""
        table = self.faceted_z3ctable_view
        column = AwakeObjectMethodColumn(self.portal, self.portal.REQUEST, table)
        # we will use the 'eea_faceted' folder as a brain
        DESCR_TEXT = u'A simple description'
        self.eea_folder.setDescription(DESCR_TEXT)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if column.attrName is not a method, it will return u''
        column.attrName = 'someUnexistingMethod'
        self.assertEquals(column.renderCell(brain), u'-')
        # now an existing method
        column.attrName = 'UID'
        self.assertEquals(column.renderCell(brain), self.eea_folder.UID())
        # we can also pass parameters
        column.attrName = 'Description'
        self.assertEquals(column.renderCell(brain), DESCR_TEXT)
        column.params = {'mimetype': 'text/html'}
        self.assertEquals(column.renderCell(brain), u'<p>{0}</p>'.format(DESCR_TEXT))

    def test_DateColumn(self):
        """This column will display a date correctly."""
        table = self.faceted_z3ctable_view
        column = DateColumn(self.portal, self.portal.REQUEST, table)
        self.eea_folder.setCreationDate('2015/05/05 12:30')
        self.eea_folder.reindexObject(idxs=['created', 'CreationDate', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no attrName, u'-' is returned
        self.assertEquals(column.renderCell(brain), u'-')
        # right, use CreationDate as attrName
        column.attrName = 'CreationDate'
        self.assertIn(column.renderCell(brain), (u'May 05, 2015', '2015-05-05'))
        # test the long_format parameter
        column.long_format = True
        self.assertIn(column.renderCell(brain), (u'May 05, 2015 12:30 PM', '2015-05-05 12:30 PM'))
        column.time_only = True
        self.assertEquals(column.renderCell(brain), u'12:30 PM')

    def test_I18nColumn(self):
        """This column will translate the value."""
        table = self.faceted_z3ctable_view
        column = I18nColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no attrName, u'-' is returned
        self.assertEquals(column.renderCell(brain), u'-')
        # right, use 'Type' as attrName
        column.attrName = 'Type'
        self.assertEquals(column.renderCell(brain), u'Folder')

    def test_BrowserViewCallColumn(self):
        """This column will call a given view and display the result."""
        table = self.faceted_z3ctable_view
        column = BrowserViewCallColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no view_name, it will raise a KeyError
        self.assertRaises(KeyError, column.renderCell, brain)
        # right, use a view_name
        column.view_name = u'testing-browsercall-view'
        self.assertEquals(column.renderCell(brain), CALL_RESULT)

    def test_VocabularyColumn(self):
        """This column uses a vocabulary to get the value to display for a given key."""
        self.eea_folder.setTitle('unexisting_key')
        self.eea_folder.reindexObject(idxs=['Title', ])
        table = self.faceted_z3ctable_view
        column = VocabularyColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # a vocabulary is required
        self.assertRaises(KeyError, column.renderCell, brain)
        # a valid vocabulary is required
        column.vocabulary = "some.unknown.vocabulary"
        self.assertRaises(KeyError, column.renderCell, brain)
        # use a valid vocabulary and test
        column.vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        # no attrName, u'-' is returned
        self.assertEquals(column.renderCell(brain), u'-')
        # an attrName but key not found in vocab, u'-' is returned
        column.attrName = 'Title'
        self.assertEquals(column.renderCell(brain), u'-')
        self.eea_folder.setTitle('existing_key')
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'Existing value')

    def test_MemberIdColumn(self):
        """This column will display the fullname of the given metadata."""
        # set a valid fullname for default user
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setProperties({'fullname': 'Full Name'})
        table = self.faceted_z3ctable_view
        column = MemberIdColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'Full Name')
        # if no value, it returns u'-'
        self.eea_folder.setCreators(u'remove_user')
        self.eea_folder.reindexObject(idxs=['Creator', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'remove_user')

    def test_ColorColumn(self):
        """A column that will just contain a CSS class made to display a color."""
        table = self.faceted_z3ctable_view
        column = ColorColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = 'getId'
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'<div title="eea_folder">&nbsp;</div>')
        # getCSSClasses depends on the 'cssClassPrefix' parameter
        self.assertEquals(column.getCSSClasses(brain), {'td': 'column_getId_eea_folder'})
        column.cssClassPrefix = 'another'
        self.assertEquals(column.getCSSClasses(brain), {'td': 'another_getId_eea_folder'})

    def test_CheckBoxColumn(self):
        """This will display a CheckBox column."""
        table = self.faceted_z3ctable_view
        column = CheckBoxColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderHeadCell(),
                          u'<input type="checkbox" id="select_unselect_items" '
                          'onClick="toggleCheckboxes(\'select_item\')" '
                          'title="Select/unselect items" checked />')
        self.assertEquals(column.renderCell(brain),
                          u'<input type="checkbox" name="select_item" value="%s" checked />' % brain.UID)
        # column could be unchecked by default
        column.checked_by_default = False
        self.assertEquals(column.renderHeadCell(),
                          u'<input type="checkbox" id="select_unselect_items" '
                          'onClick="toggleCheckboxes(\'select_item\')" '
                          'title="Select/unselect items" />')
        self.assertEquals(column.renderCell(brain),
                          u'<input type="checkbox" name="select_item" value="%s" />' % brain.UID)
        # name can be changed
        column.name = u'select_element'
        self.assertEquals(column.renderHeadCell(),
                          u'<input type="checkbox" id="select_unselect_items" '
                          'onClick="toggleCheckboxes(\'select_element\')" '
                          'title="Select/unselect items" />')
        self.assertEquals(column.renderCell(brain),
                          u'<input type="checkbox" name="select_element" value="%s" />' % brain.UID)
        # attrName can be changed
        column.attrName = 'getId'
        self.assertEquals(column.renderCell(brain),
                          u'<input type="checkbox" name="select_element" value="eea_folder" />')
        # a custom CSS class is generated
        self.assertEquals(column.getCSSClasses(brain), {'td': 'select_element_checkbox'})
