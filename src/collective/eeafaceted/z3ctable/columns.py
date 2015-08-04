# encoding: utf-8

import urllib
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from z3c.table import column
from z3c.table.header import SortingColumnHeader
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode


class BaseColumn(column.GetAttrColumn):

    sort_index = None
    # as we use setUpColumns, weight is 1 for every columns
    weight = 1
    # we can use a icon for header
    header_image = None
    # we can inject some javascript in the header
    header_js = None

    @property
    def cssClasses(self):
        """Generate a CSS class for each <th> so we can skin it if necessary."""
        return {'th': 'th_{0}'.format(self.header)}

    def getCSSClasses(self, item):
        return self.cssClasses

    def getSortKey(self, item):
        attr = self.sort_index or self.attrName
        if attr is None:
            raise ValueError('sort_index or attrName must be defined')
        return getattr(item, attr)

    def renderCell(self, item):
        return getattr(item, self.attrName.decode('utf8'))

    def _getObject(self, item):
        """Caching for getObject."""
        itemUID = item.UID
        if not hasattr(self.table, '_v_cached_objects'):
            self.table._v_cached_objects = {}
        if not itemUID in self.table._v_cached_objects:
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
                    contray_sort_order = self.table.query.get('sort_order', 'ascending') == 'ascending' and 'descending' or 'ascending'
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
                    return html.format(header, faceted_url, query_string, sort_ascending_msg, u'▲',
                                       faceted_url, query_string + '&reversed=on', sort_descending_msg, u'▼')
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
                return u'▲'
            else:
                return u'▼'
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
            return u''


class AwakeObjectMethodColumn(BaseColumn):
    """Column that will wake the object then call attrName on it."""
    # column not sortable
    sort_index = -1
    params = {}

    def renderCell(self, item):
        obj = self._getObject(item)
        try:
            result = getattr(obj, self.attrName)(**self.params)
            return safe_unicode(result)
        except AttributeError:
            return u''


class MemberIdColumn(BaseColumn):
    """ """
    attrName = 'Creator'

    def renderCell(self, item):
        membershipTool = getToolByName(self.context, 'portal_membership')
        value = self.getValue(item)
        memberInfo = membershipTool.getMemberInfo(value)
        value = memberInfo and memberInfo['fullname'] or value
        return safe_unicode(value)


class DateColumn(BaseColumn):
    """ """
    long_format = False
    time_only = False

    def renderCell(self, item):
        value = self.getValue(item)
        if not value or value == 'None':
            return u'-'
        util = getToolByName(item, 'translation_service')
        return util.ulocalized_time(value,
                                    long_format=self.long_format,
                                    time_only=self.time_only,
                                    context=item,
                                    domain='plonelocales',
                                    request=self.request)


class I18nColumn(BaseColumn):
    """GetAttrColumn which translates its content."""

    i18n_domain = 'plone'
    msgid_prefix = ''

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            return u'-'
        return translate("{0}{1}".format(self.msgid_prefix, value),
                         domain=self.i18n_domain,
                         context=self.request)


class TitleColumn(BaseColumn):
    """ """
    sort_index = 'sortable_title'

    def getSortKey(self, item):
        from Products.CMFPlone.CatalogTool import sortable_title
        return sortable_title(item)()

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            value = u'-'
        value = safe_unicode(value)
        return u'<a href="{0}">{1}</a>'.format(item.getURL(), value)


class BrowserViewCallColumn(BaseColumn):
    """A column that display the result of a given browser view name call."""
    # column not sortable
    sort_index = -1
    params = {}
    view_name = None

    def renderCell(self, item):
        if not self.view_name:
            raise KeyError('A "view_name" must be defined for column "{0}" !'.format(self.attrName))
        obj = self._getObject(item)
        return getMultiAdapter((obj, self.request), name=self.view_name)(**self.params)


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
        vocab = factory(self.context)
        value = self.getValue(item)
        if not value or not value in vocab:
            return u'-'
        else:
            return safe_unicode(vocab.getTerm(value).title)


class ColorColumn(I18nColumn):
    """A column that is aimed to display a background color and a help message on hover."""

    # no real color is applied but a generated CSS class
    cssClassPrefix = 'column'

    def renderHeadCell(self):
        """Hide the head cell."""
        return ''

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
        return u'<input type="checkbox" id="select_unselect_items" onClick="%s" title="%s" %s />' \
            % ("toggleCheckboxes('%s')" % self.name, title, self.checked_by_default and "checked" or "")

    def renderCell(self, item):
        """ """
        return u'<input type="checkbox" name="%s" value="%s" %s />' \
            % (self.name, self.getValue(item), self.checked_by_default and "checked" or "")

    def getCSSClasses(self, item):
        """ """
        return {'td': '{0}_checkbox'.format(self.name)}
