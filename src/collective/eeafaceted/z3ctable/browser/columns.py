# encoding: utf-8

from ZTUtils import make_query
from z3c.table import column
from z3c.table.header import SortingColumnHeader


class BaseColumn(column.GetAttrColumn):

    sort_index = None

    def getSortKey(self, item):
        attr = self.sort_index or self.attrName
        if attr is None:
            raise ValueError('sort_index or attrName must be defined')
        return getattr(item, attr)

    def renderCell(self, item):
        return getattr(item, self.attrName.decode('utf8'))


class BaseColumnHeader(SortingColumnHeader):

    def render(self):
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


class TitleColumn(BaseColumn):

    header = u'Titre'
    weight = 0
    sort_index = 'sortable_title'

    def getSortKey(self, item):
        from Products.CMFPlone.CatalogTool import sortable_title
        return sortable_title(item)()

    def renderCell(self, item):
        return u'<a href="{0}">{1}</a>'.format(item.getURL(),
                                               item.Title.decode('utf8'))


class AuthorColumn(BaseColumn):

    header = u'Auteur'
    attrName = 'Creator'
    weight = 10


class StateColumn(BaseColumn):

    header = u'Etat'
    attrName = 'review_state'
    weight = 20
