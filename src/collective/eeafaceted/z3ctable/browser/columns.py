# encoding: utf-8

from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from z3c.table import column
from z3c.table.header import SortingColumnHeader
from zope.i18n import translate


class BaseColumn(column.GetAttrColumn):

    sort_index = None
    # as we use setUpColumns, weight is 1 for every columns
    weight = 1

    def getSortKey(self, item):
        attr = self.sort_index or self.attrName
        if attr is None:
            raise ValueError('sort_index or attrName must be defined')
        return getattr(item, attr)

    def renderCell(self, item):
        return getattr(item, self.attrName.decode('utf8'))


class BaseColumnHeader(SortingColumnHeader):

    def render(self):
        # a column can specifically declare that it is not sortable
        # by setting sort_index to -1
        if not self.column.sort_index == -1:
            sort_on_name = self.request.get('sorting_criterion_name', '')
            if sort_on_name and (self.column.sort_index or self.column.attrName):
                html = u'<a href="{0}#{1}" title="Sort">{2} {3}</a>'
                return html.format(self.faceted_url, self.query_string,
                                   self.column.header, self.order_arrow)
        return self.column.header

    @property
    def sort_on(self):
        return self.column.sort_index or self.column.attrName

    @property
    def faceted_url(self):
        return '/'.join(self.request.get('URL').split('/')[:-1])

    @property
    def query_string(self):
        query = self.request_query
        sort_on_name = self.request.get('sorting_criterion_name', '')

        if (query.get(sort_on_name, '') == self.sort_on or
            self.table.sortOn == self.column.id) and \
           query.get('reversed', 'off') == 'off':
            query.update({'reversed': 'on'})
        elif 'reversed' in query:
            del query['reversed']
        query.update({sort_on_name: self.sort_on})
        if 'version' in query:
            del query['version']
        return make_query(query)

    @property
    def request_query(self):
        query = dict(self.request.form)
        return {k.replace('[]', ''): v for k, v in query.items()}

    @property
    def order_arrow(self):
        sort_on_name = self.request.get('sorting_criterion_name', '')
        query = self.request_query
        if query.get(sort_on_name, '') == self.sort_on or \
           self.table.sortOn == self.column.id:
            order = query.get('reversed')
            if order == 'on':
                return u'▼'
            else:
                return u'▲'
        return u''


class AwakeObjectGetAttrColumn(BaseColumn):
    """Column that will wake the object then getattr attrName on it."""
    # column not sortable
    sort_index = -1

    def renderCell(self, item):
        obj = item.getObject()
        try:
            return getattr(obj, self.attrName)
        except AttributeError:
            return u''


class AwakeObjectMethodColumn(BaseColumn):
    """Column that will wake the object then call attrName on it."""
    # column not sortable
    sort_index = -1

    def renderCell(self, item):
        obj = item.getObject()
        try:
            result = getattr(obj, self.attrName)()
            if isinstance(result, str):
                return unicode(result, 'utf-8')
        except AttributeError:
            return u''


class MemberIdColumn(BaseColumn):
    """ """
    attrName = 'Creator'

    def renderCell(self, item):
        membershipTool = getToolByName(item, 'portal_membership')
        member = membershipTool.getMemberById(self.getValue(item))
        if not member:
            return self.getValue(item)
        else:
            return membershipTool.getMemberInfo(member.getId())['fullname'] or self.getValue(item)


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

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            return u'-'
        return translate(value,
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
        if isinstance(value, str):
            value = unicode(value, 'utf-8')
        return u'<a href="{0}">{1}</a>'.format(item.getURL(), value)
