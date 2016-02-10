# encoding: utf-8

from Products.CMFPlone.utils import safe_unicode

from collective.eeafaceted.z3ctable.interfaces import IFacetedColumn
from plone import api

from z3c.table import column
from z3c.table.header import SortingColumnHeader

from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory

import urllib


class BaseColumn(column.GetAttrColumn):

    implements(IFacetedColumn)

    sort_index = None
    # as we use setUpColumns, weight is 1 for every columns
    weight = 1
    # we can use a icon for header
    header_image = None
    # we can inject some javascript in the header
    header_js = None

    @property
    def cssClasses(self):
        """Generate a default CSS class for each <th> and <td> so we can skin it if necessary."""
        return {'th': 'th_header_{0}'.format(self.attrName),
                'td': 'td_cell_{0}'.format(self.attrName), }

    def getCSSClasses(self, item):
        return self.cssClasses

    def renderCell(self, item):
        return getattr(item, self.attrName.decode('utf8'))

    def _getObject(self, item):
        """Caching for getObject."""
        itemUID = item.UID
        if not hasattr(self.table, '_v_cached_objects'):
            self.table._v_cached_objects = {}
        if itemUID not in self.table._v_cached_objects:
            self.table._v_cached_objects[itemUID] = item.getObject()

        return self.table._v_cached_objects[itemUID]


class BaseColumnHeader(SortingColumnHeader):

    def render(self):
        header = translate(self.column.header,
                           domain='collective.eeafaceted.z3ctable',
                           context=self.request)
        # header can be an image or a text
        if self.column.header_image:
            header = u'<img src="{0}/{1}" title="{2}" />'.format(self.table.portal_url,
                                                                 self.column.header_image,
                                                                 header)
        # inject some javascript in the header?
        if self.column.header_js:
            header = self.column.header_js + header
        # a column can specifically declare that it is not sortable
        # by setting sort_index to -1
        if not self.column.sort_index == -1:
            sort_on_name = self.table.sorting_criterion_name
            if sort_on_name and (self.column.sort_index or self.column.attrName):
                order_arrow = self.order_arrow
                faceted_url = self.faceted_url
                query_string = self.query_string
                if order_arrow:
                    contray_sort_order = (self.table.query.get('sort_order', 'ascending') == 'ascending'
                                          and 'descending' or 'ascending')
                    contray_sort_order_msgid = "Sort {0}".format(contray_sort_order)
                    sort_msg = translate(contray_sort_order_msgid,
                                         domain='collective.eeafaceted.z3ctable',
                                         context=self.request,
                                         default=contray_sort_order_msgid)
                    html = u'<span>{0}</span><a class="sort_arrow_enabled" href="{1}#{2}" title="{3}">{4}</a>'
                    return html.format(header, faceted_url, query_string, sort_msg, order_arrow)
                else:
                    sort_ascending_msg = translate("Sort ascending",
                                                   domain='collective.eeafaceted.z3ctable',
                                                   context=self.request,
                                                   default="Sort ascending")
                    sort_descending_msg = translate("Sort descending",
                                                    domain='collective.eeafaceted.z3ctable',
                                                    context=self.request,
                                                    default="Sort descending")
                    html = (u'<span>{0}</span><a class="sort_arrow_disabled" href="{1}#{2}" title="{3}">{4}</a>'
                            '<a class="sort_arrow_disabled" href="{5}#{6}" title="{7}"><span>{8}</span></a>')
                    return html.format(header, faceted_url, query_string, sort_ascending_msg, '&#9650;',
                                       faceted_url, query_string + '&reversed=on', sort_descending_msg,
                                       '&#9660;')
        return header

    @property
    def sort_on(self):
        return self.column.sort_index or self.column.attrName

    @property
    def faceted_url(self):
        return '/'.join(self.request.get('URL').split('/')[:-1])

    @property
    def query_string(self):
        query = self.request_query
        sort_on_name = self.table.sorting_criterion_name

        if (self.table.query.get('sort_on', '') == self.sort_on or
            self.table.sortOn == self.column.id) and \
           self.table.query.get('sort_order', 'ascending') == 'ascending':
            query.update({'reversed': 'on'})
        elif 'reversed' in query:
            del query['reversed']
        query.update({sort_on_name: self.sort_on})
        if 'version' in query:
            del query['version']
        # make sure we handle multiple valued parameters correctly
        # eea.facetednavigation needs this : ?b_start=0&c6=state1&c6=state2
        # not ?b_start=0&c6:list=state1&c6:list=state2 nor ?b_start=0&c6=state1+state2
        return urllib.urlencode(query, doseq=True)

    @property
    def request_query(self):
        query = dict(self.request.form)
        return {k.replace('[]', ''): v for k, v in query.items()}

    @property
    def order_arrow(self):
        sort_on = self.table.query.get('sort_on', '')
        sort_order = self.table.query.get('sort_order', 'ascending')
        if sort_on == self.sort_on or \
           self.table.sortOn == self.column.id:
            if sort_order == 'ascending':
                return '&#9650;'
            else:
                return '&#9660;'
        return u''


class AwakeObjectGetAttrColumn(BaseColumn):
    """Column that will wake the object then getattr attrName on it."""
    # column not sortable
    sort_index = -1

    def renderCell(self, item):
        obj = self._getObject(item)
        try:
            result = getattr(obj, self.attrName)
            return safe_unicode(result)
        except AttributeError:
            return u'-'


class AwakeObjectMethodColumn(BaseColumn):
    """Column that will wake the object then call attrName on it."""
    # column not sortable
    sort_index = -1
    params = {}
    weight = 40

    def renderCell(self, item):
        obj = self._getObject(item)
        try:
            result = getattr(obj, self.attrName)(**self.params)
            return safe_unicode(result)
        except AttributeError:
            return u'-'


class RelationTitleColumn(BaseColumn):
    """ Dexterity relation value column """

    sort_index = -1

    def getLinkedObjects(self, item):
        # z3c.relationfield.relation.RelationValue or [z3c.relationfield.relation.RelationValue, ...]
        obj = self._getObject(item)
        rels = getattr(obj, self.attrName, None)
        if not rels:
            return None
        if isinstance(rels, (list, tuple)):
            ret = []
            for rel in rels:
                if not rel.isBroken():
                    ret.append(rel.to_object)
            return ret
        elif not rels.isBroken():
            return rels.to_object
        return None

    def target_display(self, obj):
        """ Return an html link """
        return u'<a href="{0}">{1}</a>'.format(obj.absolute_url(), obj.Title().decode('utf8'))

    def renderCell(self, item):
        targets = self.getLinkedObjects(item)
        if not targets:
            return u'-'
        if isinstance(targets, (list, tuple)):
            ret = []
            for target in targets:
                ret.append(u'<li>{0}</li>'.format(self.target_display(target)))
            return u'<ul>\n{0}\n</ul>'.format('\n'.join(ret))
        else:
            return self.target_display(targets)


class MemberIdColumn(BaseColumn):
    """ """
    attrName = 'Creator'
    weight = 20

    def _get_user_fullname(self, username):
        """Get fullname without using getMemberInfo that is slow slow slow..."""
        storage = api.portal.get_tool('acl_users').mutable_properties._storage
        data = storage.get(username, None)
        if data is not None:
            return data.get('fullname', '') or username
        else:
            return username

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            return u'-'
        value = self._get_user_fullname(value)
        return safe_unicode(value)


class DateColumn(BaseColumn):
    """ """
    long_format = False
    time_only = False

    def renderCell(self, item):
        value = self.getValue(item)
        if not value or value == 'None':
            return u'-'
        return api.portal.get_localized_time(datetime=value, long_format=self.long_format, time_only=self.time_only)


class I18nColumn(BaseColumn):
    """GetAttrColumn which translates its content."""

    i18n_domain = 'plone'
    msgid_prefix = ''
    weight = 30

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            return u'-'
        return translate("{0}{1}".format(self.msgid_prefix, value),
                         domain=self.i18n_domain,
                         context=self.request)


class BrowserViewCallColumn(BaseColumn):
    """A column that display the result of a given browser view name call."""
    # column not sortable
    sort_index = -1
    params = {}
    view_name = None

    def renderCell(self, item):
        if not self.view_name:
            raise KeyError('A "view_name" must be defined for column "{0}" !'.format(self.attrName))
        return self.context.unrestrictedTraverse('{0}/{1}'.format(item.getPath(), self.view_name))(**self.params)


class VocabularyColumn(BaseColumn):
    """A column that is aware of a vocabulary and that will get value to display from it."""

    # named utility
    vocabulary = None

    def renderCell(self, item):
        if not self.vocabulary:
            raise KeyError('A "vocabulary" must be defined for column "{0}" !'.format(self.attrName))
        factory = queryUtility(IVocabularyFactory, self.vocabulary)
        if not factory:
            raise KeyError('The vocabulary "{0}" used for column "{1}" was not found !'.format(self.vocabulary,
                                                                                               self.attrName))
        value = self.getValue(item)
        if not value:
            return u'-'

        vocab = factory(self.context)
        # make sure we have an iterable
        if not hasattr(value, '__iter__'):
            value = [value]
        res = []
        for v in value:
            try:
                res.append(safe_unicode(vocab.getTerm(v).title))
            except LookupError:
                # in case an element is not in the vocabulary, add the value
                res.append(safe_unicode(v))
        return ', '.join(res)


class ColorColumn(I18nColumn):
    """A column that is aimed to display a background color and a help message on hover."""

    # no real color is applied but a generated CSS class
    cssClassPrefix = 'column'

    def renderHeadCell(self):
        """Hide the head cell."""
        return u''

    def renderCell(self, item):
        """Display a message."""
        translated_msg = super(ColorColumn, self).renderCell(item)
        return u'<div title="{0}">&nbsp;</div>'.format(translated_msg)

    def getCSSClasses(self, item):
        """Generate a CSS class to apply on the TD depending on the value."""
        return {'td': "{0}_{1}_{2}".format(self.cssClassPrefix,
                                           str(self.attrName),
                                           self.getValue(item))}


class CheckBoxColumn(BaseColumn):
    """
      Display a checkbox.
    """

    name = 'select_item'
    checked_by_default = True
    attrName = 'UID'

    def renderHeadCell(self):
        """ """
        title = translate('select_unselect_items',
                          domain='collective.eeafaceted.z3ctable',
                          context=self.request,
                          default="Select/unselect items")
        return u'<input type="checkbox" id="select_unselect_items" onClick="%s" title="%s" %s/>' \
            % ("toggleCheckboxes('%s')" % self.name, title, self.checked_by_default and "checked " or "")

    def renderCell(self, item):
        """ """
        return u'<input type="checkbox" name="%s" value="%s" %s/>' \
            % (self.name, self.getValue(item), self.checked_by_default and "checked " or "")

    def getCSSClasses(self, item):
        """ """
        return {'td': '{0}_checkbox'.format(self.name)}


class DxWidgetRenderColumn(BaseColumn):
    """A column that display the result of a dx widget."""
    # column not sortable
    sort_index = -1
    params = {}
    field_name = None
    view_name = 'view'
    prefix = None

    def renderCell(self, item):
        if not self.field_name:
            raise KeyError('A "field_name" must be defined for column "{0}" !'.format(self.attrName))
        view = self.context.restrictedTraverse('{0}/{1}'.format(item.getPath(), self.view_name))
        view.updateFieldsFromSchemata()
        # to increase velocity, we escape all other fields. Faster than making new field.Fields
        for field in view.fields:
            if field != self.field_name:
                view.fields = view.fields.omit(field)
        # we update the widgets for the kept field
        # passing a string parameter that can be used in overrided updateWidgets
        # to know that we are in this particular rendering case
        view.updateWidgets(prefix=self.prefix)
        try:
            widget = view.widgets[self.field_name]
        except KeyError:
            raise KeyError('The field_name "{0}" is not available for column "{1}" !'.format(self.field_name,
                                                                                             self.attrName))
        return widget.render()  # unicode


############################################################
#      Custom columns                                   ####
############################################################
class CreationDateColumn(DateColumn):
    """ """
    sort_index = 'created'
    weight = 10
    long_format = True


class ModificationDateColumn(DateColumn):
    """ """
    sort_index = 'modified'
    weight = 10
    long_format = True


class TitleColumn(BaseColumn):
    """ """
    sort_index = 'sortable_title'
    weight = 0

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            value = u'-'
        value = safe_unicode(value)
        return u'<a href="{0}">{1}</a>'.format(item.getURL(), value)
