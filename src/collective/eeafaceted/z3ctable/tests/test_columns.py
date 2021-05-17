# -*- coding: utf-8 -*-

from collective.eeafaceted.z3ctable.columns import AbbrColumn
from collective.eeafaceted.z3ctable.columns import ActionsColumn
from collective.eeafaceted.z3ctable.columns import AwakeObjectGetAttrColumn
from collective.eeafaceted.z3ctable.columns import AwakeObjectMethodColumn
from collective.eeafaceted.z3ctable.columns import BaseColumn
from collective.eeafaceted.z3ctable.columns import BooleanColumn
from collective.eeafaceted.z3ctable.columns import BrowserViewCallColumn
from collective.eeafaceted.z3ctable.columns import CheckBoxColumn
from collective.eeafaceted.z3ctable.columns import ColorColumn
from collective.eeafaceted.z3ctable.columns import DateColumn
from collective.eeafaceted.z3ctable.columns import DxWidgetRenderColumn
from collective.eeafaceted.z3ctable.columns import ElementNumberColumn
from collective.eeafaceted.z3ctable.columns import I18nColumn
from collective.eeafaceted.z3ctable.columns import IconsColumn
from collective.eeafaceted.z3ctable.columns import MemberIdColumn
from collective.eeafaceted.z3ctable.columns import PrettyLinkWithAdditionalInfosColumn
from collective.eeafaceted.z3ctable.columns import RelationPrettyLinkColumn
from collective.eeafaceted.z3ctable.columns import RelationTitleColumn
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.tests.views import CALL_RESULT
from datetime import date
from datetime import datetime
from imio.prettylink.interfaces import IPrettyLink
from plone import api
from plone.app.testing import login
from plone.batching import Batch
from z3c.relationfield.relation import RelationValue
from z3c.table.interfaces import IColumn
from z3c.table.table import Table
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.intid.interfaces import IIntIds


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
        - Text;
        - select_row.
        """
        self.faceted_z3ctable_view.initColumns()
        default_columns = sorted([col.__name__ for col in self.faceted_z3ctable_view.columns])
        self.assertEqual(
            default_columns,
            [u'CreationDate',
             u'Creator',
             u'ModificationDate',
             u'Title',
             u'actions',
             u'getText',
             u'pretty_link',
             u'review_state',
             u'select_row'])

    def test_BaseColumn(self):
        """Test the BaseColumn behavior and changes regarding default z3c.table column."""
        table = self.faceted_z3ctable_view
        column = BaseColumn(self.portal, self.portal.REQUEST, table)
        # we will use the 'eea_faceted' folder as a brain
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # the table is in charge of generating correct column name and header
        table.nameColumn(column, 'Title')
        self.assertEqual(column.__name__, u'Title')
        self.assertEqual(column.header, u'header_Title')
        # a CSS class for <TH> and <TD> is generated using the attrName
        self.assertEqual(column.cssClasses,
                         {'th': 'th_header_Title',
                          'td': 'td_cell_Title'})
        # a method getCSSClasses receiving a brain is implemented
        # by default it returns cssClasses but it is made to be overrided
        self.assertEqual(column.getCSSClasses(brain), column.cssClasses)
        self.assertEqual(column.renderCell(brain), brain.Title)

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
        self.assertEqual(column.renderHeadCell(),
                         u'<span>Title</span><a class="sort_arrow_disabled" '
                         u'href="http:/#c2=sortable_title" title="Sort ascending">&#9650;</a><a '
                         u'class="sort_arrow_disabled" href="http:/#c2=sortable_title&reversed=on" '
                         u'title="Sort descending"><span>&#9660;</span></a>')
        # if column.sort_index = -1, it means that it is not sortable, header is rendered accordingly
        column.sort_index = -1
        # header_Title translated
        self.assertEqual(column.renderHeadCell(), u'Title')
        # we may also inject JS in the header using column.header_js
        column.header_js = '<script type="text/javascript">console.log("Hello world!");</script>'
        self.assertEqual(column.renderHeadCell(),
                         u'<script type="text/javascript">console.log("Hello world!");</script>Title')
        # we may also use an image as header using column.header_image
        # remove header_js to ease test reading although this can be used together
        column.header_js = u''
        column.header_image = 'image.png'
        self.assertEqual(column.renderHeadCell(),
                         u'<img src="http://nohost/plone/image.png" title="Title" />')
        # define a help message
        column.header_help = u'My help message'
        self.assertEqual(column.renderHeadCell(),
                         u'<acronym title="My help message">'
                         u'<img src="http://nohost/plone/image.png" title="Title" />'
                         u'</acronym>')

    def test_AwakeObjectGetAttrColumn(self):
        """This will wake the given catalog brain and getattr the attrName on it.
           This is used when displaying in a column an attribute that is not a catalog metadata."""
        table = self.faceted_z3ctable_view
        column = AwakeObjectGetAttrColumn(self.portal, self.portal.REQUEST, table)
        # we will use the 'eea_faceted' folder as a brain
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if column.attrName is not an attribute, it will return u''
        column.attrName = 'someUnexistingAttribute'
        self.assertEqual(column.renderCell(brain), u'-')
        # now an existing attribute
        column.attrName = '_at_uid'
        self.assertEqual(column.renderCell(brain), self.eea_folder._at_uid)

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
        self.assertEqual(column.renderCell(brain), u'-')
        # now an existing method
        column.attrName = 'UID'
        self.assertEqual(column.renderCell(brain), self.eea_folder.UID())
        # we can also pass parameters
        column.attrName = 'Description'
        self.assertEqual(column.renderCell(brain), DESCR_TEXT)
        column.params = {'mimetype': 'text/html'}
        self.assertEqual(column.renderCell(brain), u'<p>{0}</p>'.format(DESCR_TEXT))

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
        column.use_caching = False
        # test with a DateTime attribute
        self.eea_folder.setCreationDate('2015/05/05 12:30')
        self.eea_folder.reindexObject(idxs=['created', 'CreationDate', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no attrName, u'-' is returned
        self.assertEqual(column.renderCell(brain), u'-')
        # right, use CreationDate as attrName
        column.attrName = 'CreationDate'
        self.assertIn(column.renderCell(brain), (u'May 05, 2015', '2015-05-05'))
        # test with an ignored value
        column.ignored_value = brain.CreationDate
        self.assertEqual(column.renderCell(brain), u'-')
        column.ignored_value = None
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
        self.assertEqual(column.renderCell(self.eea_folder), u'')

    def test_I18nColumn(self):
        """This column will translate the value."""
        table = self.faceted_z3ctable_view
        column = I18nColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no attrName, u'-' is returned
        self.assertEqual(column.renderCell(brain), u'-')
        # right, use 'Type' as attrName
        column.attrName = 'Type'
        self.assertEqual(column.renderCell(brain), u'Folder')

    def test_BooleanColumn(self):
        """This column will translate the values False or True."""
        table = self.faceted_z3ctable_view
        column = BooleanColumn(self.portal, self.portal.REQUEST, table)
        tt = api.content.create(
            container=self.eea_folder,
            type='testingtype',
            title='My testing type')
        folderish_brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        not_folderish_brain = self.portal.portal_catalog(UID=tt.UID())[0]
        column.attrName = 'is_folderish'
        self.assertEqual(column.renderCell(folderish_brain), 'boolean_value_True')
        self.assertEqual(column.renderCell(not_folderish_brain), 'boolean_value_False')

    def test_BrowserViewCallColumn(self):
        """This column will call a given view and display the result."""
        table = self.faceted_z3ctable_view
        column = BrowserViewCallColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # if no view_name, it will raise a KeyError
        self.assertRaises(KeyError, column.renderCell, brain)
        # right, use a view_name
        column.view_name = u'testing-browsercall-view'
        self.assertEqual(column.renderCell(brain), CALL_RESULT)

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
        self.assertEqual(api.content.get_state(self.eea_folder), 'private')
        self.assertEqual(api.content.get_state(subfolder), 'published')
        # eea_folder is not viewable by a Member but subfolder is viewable
        new_user = api.user.create('test@test.be', 'new_user', 'Password_12')
        login(self.portal, new_user.getId())
        self.assertFalse(api.user.has_permission('View', user=new_user, obj=self.eea_folder))
        self.assertTrue(api.user.has_permission('View', user=new_user, obj=subfolder))
        # call the column
        brain = self.portal.portal_catalog(UID=subfolder.UID())[0]
        column.view_name = u'testing-browsercall-view'
        self.assertEqual(column.renderCell(brain), CALL_RESULT)

    def test_VocabularyColumn(self):
        """This column uses a vocabulary to get the value to display for a given key."""
        self.eea_folder.setTitle(u'unexisting_key')
        self.eea_folder.reindexObject(idxs=['Title', ])
        table = self.faceted_z3ctable_view
        column = VocabularyColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # no attrName, u'-' is returned
        self.assertEqual(column.renderCell(brain), u'-')

        column.attrName = 'Title'
        # a vocabulary is required
        self.assertRaises(KeyError, column.renderCell, brain)
        # a valid vocabulary is required
        column.vocabulary = "some.unknown.vocabulary"
        self.assertRaises(KeyError, column.renderCell, brain)
        # use a valid vocabulary and test
        column.vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"

        # mono valued vocabulary
        # an attrName but key not found in vocab, the key is returned
        self.assertEqual(column.renderCell(brain), u'unexisting_key')
        # existing key
        self.eea_folder.setTitle('existing_key1')
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain), u'Existing v\xe9lue 1')

        # multiValued vocabulary
        self.eea_folder.setTitle(('existing_key1', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain), u'Existing v\xe9lue 1, Existing v\xe9lue 2')
        # mixed with unexisting key
        self.eea_folder.setTitle(('existing_key1', 'unexisting_key', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u'Existing v\xe9lue 1, unexisting_key, Existing v\xe9lue 2')

    def test_AbbrColumn(self):
        """This column uses 2 vocabularies to generate an <abbr> tag where first vocabulary
           if the displayed value (abbreviation) and second vocabulary (full_vocabulary)
           displays the full value."""
        self.eea_folder.setTitle(u'unexisting_key')
        self.eea_folder.reindexObject(idxs=['Title', ])
        table = self.faceted_z3ctable_view
        column = AbbrColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        # not value, '-' is returned
        self.assertEqual(column.renderCell(brain), u'-')
        column.attrName = 'Title'
        # both vocabularies are required
        column.vocabulary = None
        column.full_vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        with self.assertRaises(KeyError) as cm:
            column.renderCell(brain)
        self.assertEqual(
            cm.exception.message,
            'A "vocabulary" and a "full_vocabulary" must be defined for column "Title" !')
        column.vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        column.full_vocabulary = None
        with self.assertRaises(KeyError) as cm:
            column.renderCell(brain)
        self.assertEqual(
            cm.exception.message,
            'A "vocabulary" and a "full_vocabulary" must be defined for column "Title" !')

        # both vocabularies must be valid
        column.vocabulary = "some.unknown.vocabulary"
        column.full_vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        self.assertRaises(KeyError, column.renderCell, brain)
        column.vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        column.full_vocabulary = "some.unknown.vocabulary"
        self.assertRaises(KeyError, column.renderCell, brain)

        # use a valid vocabulary and test
        column.vocabulary = "collective.eeafaceted.z3ctable.testingvocabulary"
        column.full_vocabulary = "collective.eeafaceted.z3ctable.testingfullvocabulary"
        self.assertEqual(column.renderCell(brain), u'unexisting_key')

        # mono valued vocabulary
        # an attrName but key not found in vocab, the key is returned
        self.assertEqual(column.renderCell(brain), u'unexisting_key')
        # existing key
        self.eea_folder.setTitle('existing_key1')
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u"<abbr title='Full existing value 1'>Existing v\xe9lue 1</abbr>")

        # multiValued vocabulary
        self.eea_folder.setTitle(('existing_key1', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u"<abbr title='Full existing value 1'>Existing v\xe9lue 1</abbr>, "
                         u"<abbr title='Full existing value 2'>Existing v\xe9lue 2</abbr>")
        # mixed with unexisting key
        self.eea_folder.setTitle(('existing_key1', 'unexisting_key', 'existing_key2'))
        self.eea_folder.reindexObject(idxs=['Title', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u"<abbr title='Full existing value 1'>Existing v\xe9lue 1</abbr>, "
                         u"unexisting_key, "
                         u"<abbr title='Full existing value 2'>Existing v\xe9lue 2</abbr>")

    def test_MemberIdColumn(self):
        """This column will display the fullname of the given metadata."""
        # set a valid fullname for default user
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setProperties({'fullname': 'Full Name'})
        table = self.faceted_z3ctable_view
        column = MemberIdColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain), u'Full Name')
        # if user is not found, the stored value is returned
        self.eea_folder.setCreators(u'removed_user')
        self.eea_folder.reindexObject(idxs=['Creator', ])
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain), u'removed_user')
        # if no value, it returns u'-'
        # memberId taken into account could be in any brain metadata, use Description
        column.attrName = 'Description'
        self.assertEqual(brain.Description, '')
        self.assertEqual(column.renderCell(brain), u'-')

    def test_ColorColumn(self):
        """A column that will just contain a CSS class made to display a color."""
        table = self.faceted_z3ctable_view
        column = ColorColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = 'getId'
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain), u'<div title="eea_folder">&nbsp;</div>')
        # getCSSClasses depends on the 'cssClassPrefix' parameter
        self.assertEqual(column.getCSSClasses(brain), {'td': 'column_getId_eea_folder'})
        column.cssClassPrefix = 'another'
        self.assertEqual(column.getCSSClasses(brain), {'td': 'another_getId_eea_folder'})
        # no header is displayed for a ColorColumn
        self.assertTrue(column.renderHeadCell().startswith("<span>&nbsp;&nbsp;&nbsp;</span>"))

    def test_CheckBoxColumn(self):
        """This will display a CheckBox column."""
        table = self.faceted_z3ctable_view
        column = CheckBoxColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderHeadCell(),
                         u'<input type="checkbox" id="select_unselect_items" '
                         u'onClick="toggleCheckboxes(\'select_item\')" '
                         u'title="Select/unselect all" name="select_item" checked />')
        self.assertEqual(column.renderCell(brain),
                         u'<label class="select-item-label">'
                         u'<input type="checkbox" name="select_item" value="%s" checked />'
                         u'</label>' % brain.UID)
        # column could be unchecked by default
        column.checked_by_default = False
        self.assertEqual(column.renderHeadCell(),
                         u'<input type="checkbox" id="select_unselect_items" '
                         u'onClick="toggleCheckboxes(\'select_item\')" '
                         u'title="Select/unselect all" name="select_item" />')
        self.assertEqual(column.renderCell(brain),
                         u'<label class="select-item-label">'
                         u'<input type="checkbox" name="select_item" value="%s" />'
                         u'</label>' % brain.UID)
        # name can be changed
        column.name = u'select_element'
        self.assertEqual(column.renderHeadCell(),
                         u'<input type="checkbox" id="select_unselect_items" '
                         u'onClick="toggleCheckboxes(\'select_element\')" '
                         u'title="Select/unselect all" name="select_element" />')
        self.assertEqual(column.renderCell(brain),
                         u'<label class="select-item-label">'
                         u'<input type="checkbox" name="select_element" value="%s" />'
                         u'</label>' % brain.UID)
        # attrName can be changed
        column.attrName = 'getId'
        self.assertEqual(column.renderCell(brain),
                         u'<label class="select-item-label">'
                         u'<input type="checkbox" name="select_element" value="eea_folder" />'
                         u'</label>')
        # a custom CSS class is generated
        self.assertEqual(column.getCSSClasses(brain), {'td': 'select_element_checkbox'})

    def test_TitleColumn(self):
        """A base column using 'Title' metadata but rendered as a link to the element."""
        table = self.faceted_z3ctable_view
        # this column is defined in ZCML
        column = queryMultiAdapter((self.eea_folder, self.eea_folder.REQUEST, table), IColumn, 'Title')
        # attrName is set during table.setUpColumns
        column.attrName = 'Title'
        # this column use 'sortable_title' as sort_index
        self.assertEqual(column.sort_index, 'sortable_title')
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u'<a href="{0}">{1}</a>'.format(brain.getURL(), brain.Title))
        # if brain has no Title, '-' is used
        brain.Title = ''
        self.assertEqual(column.renderCell(brain), u'<a href="{0}">-</a>'.format(brain.getURL()))

    def test_PrettyLinkColumn(self):
        """A base column rendering imio.prettylink."""
        table = self.faceted_z3ctable_view
        # this column is defined in ZCML
        column = queryMultiAdapter((self.eea_folder, self.eea_folder.REQUEST, table), IColumn, 'pretty_link')
        # attrName is set during table.setUpColumns
        column.attrName = 'Title'
        table.nameColumn(column, 'Title')
        # this column use 'sortable_title' as sort_index
        self.assertEqual(column.sort_index, 'sortable_title')
        brain = self.portal.portal_catalog(UID=self.eea_folder.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         IPrettyLink(self.eea_folder).getLink())
        # a pretty_link class is defined for the th
        self.assertEqual(column.cssClasses, {'td': 'pretty_link', 'th': 'th_header_Title'})

    def test_PrettyLinkWithAdditionalInfosColumn(self):
        """A base column rendering imio.prettylink and additional informations."""
        table = self.faceted_z3ctable_view
        column = PrettyLinkWithAdditionalInfosColumn(self.portal, self.portal.REQUEST, table)
        # attrName is set during table.setUpColumns
        column.attrName = 'Title'
        # this column use 'sortable_title' as sort_index
        self.assertEqual(column.sort_index, 'sortable_title')
        # this column only works with DX content types
        tt = api.content.create(
            container=self.eea_folder,
            type='testingtype',
            title='My testing type',
            description='My description',
            bool_field=False)
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        # no additional informations defined so nothing more than pretty link is returned
        self.assertTrue(column.renderCell(brain).startswith(IPrettyLink(tt).getLink()))
        # define some informations
        tt.afield = u'My field content'
        rendered = column.renderCell(brain)
        self.assertTrue(
            '<span id="form-widgets-afield" class="text-widget textline-field">My field content</span>'
            in rendered)
        # ai_extra_fields, by default id, UID and description
        self.assertTrue(
            '<div class="discreet"><label class="horizontal">Id</label>'
            '<div class="type-textarea-widget">my-testing-type</div></div>'
            in rendered)
        self.assertTrue(
            '<div class="discreet"><label class="horizontal">Uid</label>'
            '<div class="type-textarea-widget">{0}</div></div>'.format(brain.UID)
            in rendered)
        self.assertTrue(
            '<div class="discreet"><label class="horizontal">Description</label>'
            '<div class="type-textarea-widget">My description</div></div>'
            in rendered)

    def test_RelationPrettyLinkColumn(self):
        """Test the RelationPrettyLinkColumn, it will render IPrettyLink.getLink."""
        table = self.faceted_z3ctable_view
        column = RelationPrettyLinkColumn(self.portal, self.portal.REQUEST, table)
        fold1 = api.content.create(container=self.portal, type='Folder', id='fold1', title="Folder 1")
        fold2 = api.content.create(container=self.portal, type='Folder', id='fold2', title="Folder 2")
        intids = getUtility(IIntIds)
        rel1 = RelationValue(intids.getId(fold1))
        rel2 = RelationValue(intids.getId(fold2))
        tt = api.content.create(container=self.portal, type='testingtype', id='testingtype',
                                title='My testing type', rel_item=rel1, rel_items=[rel1, rel2])
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        column.attrName = 'rel_item'
        self.assertEqual(u"<a class='pretty_link' title='Folder 1' "
                         u"href='http://nohost/plone/fold1' target='_self'>"
                         u"<span class='pretty_link_content state-private'>Folder 1</span></a>",
                         column.renderCell(brain))
        column.params = {'showContentIcon': True}
        self.assertEqual(u"<a class='pretty_link' title='Folder 1' "
                         u"href='http://nohost/plone/fold1' target='_self'>"
                         u"<span class='pretty_link_content state-private contenttype-Folder'>Folder 1</span></a>",
                         column.renderCell(brain))
        column.params = {}
        column.attrName = 'rel_items'
        self.assertEqual(u"<ul>\n<li><a class='pretty_link' title='Folder 1' href='http://nohost/plone/fold1' "
                         u"target='_self'><span class='pretty_link_content state-private'>Folder 1</span></a></li>\n"
                         u"<li><a class='pretty_link' title='Folder 2' href='http://nohost/plone/fold2' "
                         u"target='_self'><span class='pretty_link_content state-private'>Folder 2</span></a></li>\n"
                         u"</ul>",
                         column.renderCell(brain))
        # a pretty_link class is defined for the td
        table.nameColumn(column, 'rel_items')
        self.assertEqual(column.cssClasses, {'td': 'pretty_link', 'th': 'th_header_rel_items'})

    def test_ActionsColumn(self):
        """Render the @@actions_panel view."""
        table = self.faceted_z3ctable_view
        column = ActionsColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.portal.eea_folder.UID())[0]
        # it is a BrowserViewCallColumn with some fixed parameters
        self.assertEqual(column.view_name, 'actions_panel')
        rendered_column = column.renderCell(brain)
        # common parts are there : 'edit', 'Delete', 'history'
        self.assertIn("/edit", rendered_column)
        self.assertIn("javascript:confirmDeleteObject", rendered_column)
        self.assertIn("history.gif", rendered_column)

    def test_ElementNumberColumn(self):
        """A base column using 'Title' metadata but rendered as a link to the element."""
        # create some testingtype instances to build a batch
        for i in range(0, 8):
            api.content.create(container=self.eea_folder,
                               type='testingtype',
                               title='My testing type {0}'.format(i))
        # create a batch with every elements
        brains = self.portal.portal_catalog(portal_type='testingtype')
        self.assertEqual(len(brains), 8)

        # without batch
        table = BrainsWithoutBatchTable(self.portal, self.portal.REQUEST)
        self.assertEqual(len(table.values), 8)
        column = ElementNumberColumn(self.portal, self.portal.REQUEST, table)
        self.assertEqual(column.renderCell(table.values[0]), 1)
        self.assertEqual(column.renderCell(table.values[1]), 2)
        self.assertEqual(column.renderCell(table.values[2]), 3)
        self.assertEqual(column.renderCell(table.values[3]), 4)
        self.assertEqual(column.renderCell(table.values[4]), 5)
        self.assertEqual(column.renderCell(table.values[5]), 6)
        self.assertEqual(column.renderCell(table.values[6]), 7)
        self.assertEqual(column.renderCell(table.values[7]), 8)

        # with batch
        table = self.faceted_z3ctable_view
        column = ElementNumberColumn(self.portal, self.portal.REQUEST, table)
        batch = Batch(brains, size=5)
        table.update(batch)
        self.assertEqual(batch.start, 1)
        self.assertEqual(column.renderCell(batch._sequence[0]), 1)
        self.assertEqual(column.renderCell(batch._sequence[1]), 2)
        self.assertEqual(column.renderCell(batch._sequence[2]), 3)
        self.assertEqual(column.renderCell(batch._sequence[3]), 4)
        self.assertEqual(column.renderCell(batch._sequence[4]), 5)
        # next 5 others (3 last actually) are accessible if batch start changed
        self.assertRaises(ValueError, column.renderCell, batch._sequence[5])
        batch.start = 6
        self.assertEqual(column.renderCell(batch._sequence[5]), 6)
        self.assertEqual(column.renderCell(batch._sequence[6]), 7)
        self.assertEqual(column.renderCell(batch._sequence[7]), 8)

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
        self.assertIn(
            '<span id="form-widgets-afield" class="text-widget textline-field">This is a text line</span>',
            column.renderCell(brain))

    def test_js_variables(self):
        """Some JS variables are defined for translation purpose."""
        js_variables = self.portal.restrictedTraverse(
            'collective_eeafaceted_z3ctable_js_variables.js')
        self.assertEqual(
            js_variables(),
            'var no_selected_items = "Please select at least one element.";\n')

    def test_IconsColumn(self):
        table = self.faceted_z3ctable_view
        column = IconsColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = u'Subject'
        tt = api.content.create(container=self.eea_folder, type='testingtype',
                                id='testingtype', title='My testing type', subject=(u'01', u'02'))
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        self.assertEqual(column.renderCell(brain),
                         u'<img title="01" class="" src="http://nohost/plone/01" /> '
                         u'<img title="02" class="" src="http://nohost/plone/02" />')


class BrainsWithoutBatchTable(Table):
    """ """
    @property
    def values(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(portal_type='testingtype')
