# -*- coding: utf-8 -*-

from datetime import datetime, date
from plone.app.testing import login
from zope.component import queryMultiAdapter, getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue
from z3c.table.interfaces import IColumn

from plone import api
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.columns import AwakeObjectGetAttrColumn
from collective.eeafaceted.z3ctable.columns import AwakeObjectMethodColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import RelationTitleColumn
from collective.eeafaceted.z3ctable.columns import BrowserViewCallColumn
from collective.eeafaceted.z3ctable.columns import CheckBoxColumn
from collective.eeafaceted.z3ctable.columns import ColorColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import I18nColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.eeafaceted.z3ctable.columns import DxWidgetRenderColumn
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

    def test_BaseColumn(self):
        """Test the BaseColumn behavior and changes regarding default z3c.table column."""
        table = self.faceted_z3ctable_view
        column = BaseColumn(self.portal, self.portal.REQUEST, table)
        # we will use the 'eea_faceted' folder as a brain
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # the table is in charge of generating correct column name and header
        table.nameColumn(column, 'Title')
        self.assertEquals(column.__name__, u'Title')
        self.assertEquals(column.header, u'header_Title')
        # a CSS class for <TH> and <TD> is generated using the attrName
        self.assertEquals(column.cssClasses,
                          {'th': 'th_header_Title',
                           'td': 'td_cell_Title'})
        # a method getCSSClasses receiving a brain is implemented
        # by default it returns cssClasses but it is made to be overrided
        self.assertEquals(column.getCSSClasses(brain), column.cssClasses)
        self.assertEquals(column.renderCell(brain), brain.Title)

    def test_HeaderColumn(self):
        """The header will behave correctly with the faceted query, especially regarding sorting."""
        table = self.faceted_z3ctable_view
        # use the CreationDateC
        column = BaseColumn(self.portal, self.portal.REQUEST, table)
        table.nameColumn(column, 'Title')
        # if column is sortable, header is rendered with relevant arrows
        column.sort_index = 'sortable_title'
        # render the headerCell
        self.maxDiff = None
        self.assertEquals(column.renderHeadCell(),
                          u'<span>header_Title</span><a class="sort_arrow_disabled" '
                          u'href="http:/#c2=sortable_title" title="Sort ascending">&#9650;</a><a '
                          u'class="sort_arrow_disabled" href="http:/#c2=sortable_title&reversed=on" '
                          u'title="Sort descending"><span>&#9660;</span></a>')
        # if column.sort_index = -1, it means that it is not sortable, header is rendered accordingly
        column.sort_index = -1
        self.assertEquals(column.renderHeadCell(), u'header_Title')
        # we may also inject JS in the header using column.header_js
        column.header_js = '<script type="text/javascript">console.log("Hello world!");</script>'
        self.assertEquals(column.renderHeadCell(),
                          u'<script type="text/javascript">console.log("Hello world!");</script>header_Title')
        # we may also use an image as header using column.header_image
        # remove header_js to ease test reading although this can be used together
        column.header_js = u''
        column.header_image = 'image.png'
        self.assertEquals(column.renderHeadCell(),
                          u'<img src="http://nohost/plone/image.png" title="header_Title" />')

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

    def test_RelationTitleColumn(self):
        """ """
        table = self.faceted_z3ctable_view
        column = RelationTitleColumn(self.portal, self.portal.REQUEST, table)
        intids = getUtility(IIntIds)
        fold1 = api.content.create(container=self.portal, type='Folder', id='fold1', title="Folder 1")
        fold2 = api.content.create(container=self.portal, type='Folder', id='fold2', title="Folder 2")
        rel1 = RelationValue(intids.getId(fold1))
        rel2 = RelationValue(intids.getId(fold2))
        tt = api.content.create(container=self.eea_folder, type='testingtype',
                                id='testingtype', title='My testing type', rel_item=rel1,
                                rel_items=[rel1, rel2])
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        column.attrName = 'rel_item'
        self.assertEqual(u'<a href="http://nohost/plone/fold1">Folder 1</a>',
                         column.renderCell(brain))
        column.attrName = 'rel_items'
        self.assertEqual(u'<ul>\n<li><a href="http://nohost/plone/fold1">Folder 1</a></li>\n'
                         '<li><a href="http://nohost/plone/fold2">Folder 2</a></li>\n</ul>',
                         column.renderCell(brain))

    def test_DateColumn(self):
        """This column will display a date correctly."""
        table = self.faceted_z3ctable_view
        column = DateColumn(self.portal, self.portal.REQUEST, table)
        # test with a DateTime attribute
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
        self.assertIn(column.renderCell(brain), (u'May 05, 2015 12:30 PM', '2015-05-05 12:30'))
        column.time_only = True
        self.assertIn(column.renderCell(brain), (u'12:30', u'12:30 PM'))
        # test with a datetime attribute
        self.eea_folder.a_datetime = datetime(2015, 05, 06, 12, 30)
        column.attrName = 'a_datetime'
        column.long_format = False
        column.time_only = False
        self.assertIn(column.renderCell(self.eea_folder), (u'May 06, 2015', '2015-05-06'))
        column.long_format = True
        self.assertIn(column.renderCell(self.eea_folder), (u'May 06, 2015 12:30 PM', '2015-05-06 12:30'))
        column.time_only = True
        self.assertIn(column.renderCell(self.eea_folder), (u'12:30', u'12:30 PM'))
        # test with a date attribute
        self.eea_folder.a_date = date(2015, 05, 07)
        column.attrName = 'a_date'
        column.long_format = False
        column.time_only = False
        self.assertIn(column.renderCell(self.eea_folder), (u'May 07, 2015', '2015-05-07'))
        column.long_format = True
        self.assertIn(column.renderCell(self.eea_folder), (u'May 07, 2015', '2015-05-07'))
        column.time_only = True
        self.assertEquals(column.renderCell(self.eea_folder), u'')

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

    def test_BrowserViewCallColumnContextWithPrivateSublevels(self):
        """Test that using the column works if some sublevels of the
           used context are not viewable by the current user."""
        table = self.faceted_z3ctable_view
        column = BrowserViewCallColumn(self.portal, self.portal.REQUEST, table)
        # create a subFolder in the eea_folder, and publish it
        subfolder = api.content.create(container=self.eea_folder,
                                       type='Folder',
                                       id='subfolder',
                                       title='Subfolder')
        api.content.transition(subfolder, 'publish')
        self.assertEquals(api.content.get_state(self.eea_folder), 'private')
        self.assertEquals(api.content.get_state(subfolder), 'published')
        # eea_folder is not viewable by a Member but subfolder is viewable
        new_user = api.user.create('test@test.be', 'new_user', 'Password_12')
        login(self.portal, new_user.getId())
        self.assertFalse(api.user.has_permission('View', user=new_user, obj=self.eea_folder))
        self.assertTrue(api.user.has_permission('View', user=new_user, obj=subfolder))
        # call the column
        brain = self.portal.portal_catalog(UID=subfolder.UID())[0]
        column.view_name = u'testing-browsercall-view'
        self.assertEquals(column.renderCell(brain), CALL_RESULT)

    def test_VocabularyColumn(self):
        """This column uses a vocabulary to get the value to display for a given key."""
        self.eea_folder.setTitle(u'unexisting_key')
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

        # mono valued vocabulary
        # an attrName but key not found in vocab, the key is returned
        column.attrName = 'Title'
        self.assertEquals(column.renderCell(brain), u'unexisting_key')
        # existing key
        self.eea_folder.setTitle('existing_key1')
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'Existing value 1')

        # multiValued vocabulary
        self.eea_folder.setTitle(('existing_key1', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'Existing value 1, Existing value 2')
        # mixed with unexisting key
        self.eea_folder.setTitle(('existing_key1', 'unexisting_key', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain),
                          u'Existing value 1, unexisting_key, Existing value 2')

    def test_MemberIdColumn(self):
        """This column will display the fullname of the given metadata."""
        # set a valid fullname for default user
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setProperties({'fullname': 'Full Name'})
        table = self.faceted_z3ctable_view
        column = MemberIdColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'Full Name')
        # if user is not found, the stored value is returned
        self.eea_folder.setCreators(u'removed_user')
        self.eea_folder.reindexObject(idxs=['Creator', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'removed_user')
        # if no value, it returns u'-'
        # memberId taken into account could be in any brain metadata, use Description
        column.attrName = 'Description'
        self.assertEquals(brain.Description, '')
        self.assertEquals(column.renderCell(brain), u'-')

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
        # no header is displayed for a ColorColumn
        self.assertEquals(column.renderHeadCell(), u'')

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

    def test_TitleColumn(self):
        """A base column using 'Title' metadata but rendered as a link to the element."""
        table = self.faceted_z3ctable_view
        # this column is defined in ZCML
        column = queryMultiAdapter((self.eea_folder, self.eea_folder.REQUEST, table), IColumn, 'Title')
        # attrName is set during table.setUpColumns
        column.attrName = 'Title'
        # this column use 'sortable_title' as sort_index
        self.assertEquals(column.sort_index, 'sortable_title')
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEquals(column.renderCell(brain), u'<a href="{0}">{1}</a>'.format(brain.getURL(),
                                                                                    brain.Title))
        # if brain has no Title, and simple '-' is used
        brain.Title = ''
        self.assertEquals(column.renderCell(brain), u'<a href="{0}">-</a>'.format(brain.getURL()))

    def test_DxWidgetRenderColumn(self):
        """This column display a field widget rendering."""
        table = self.faceted_z3ctable_view
        column = DxWidgetRenderColumn(self.portal, self.portal.REQUEST, table)
        tt = api.content.create(container=self.eea_folder, type='testingtype',
                                id='testingtype', title='My testing type', afield='This is a text line')
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        self.assertRaises(KeyError, column.renderCell, brain)
        column.field_name = 'IBasic.title'
        self.assertRaises(KeyError, column.renderCell, brain)
        column.field_name = 'afield'
        self.assertIn('<span id="form-widgets-afield" class="text-widget textline-field">This is a text line</span>',
                      column.renderCell(brain))
