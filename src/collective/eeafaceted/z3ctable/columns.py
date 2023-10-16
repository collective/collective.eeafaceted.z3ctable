# encoding: utf-8

from collective.eeafaceted.z3ctable import _
from collective.eeafaceted.z3ctable.interfaces import IFacetedColumn
from collective.excelexport.exportables.dexterityfields import get_exportable_for_fieldname
from datetime import date
from DateTime import DateTime
from imio.helpers.content import base_getattr
from imio.helpers.content import get_user_fullname
from plone import api
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IDataManager
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from z3c.table import column
from z3c.table.header import SortingColumnHeader
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory

import html
import os
import pkg_resources
import urllib


try:
    api.env.get_distribution('imio.prettylink')
    from imio.prettylink.interfaces import IPrettyLink
    HAS_PRETTYLINK = True
except pkg_resources.DistributionNotFound:
    HAS_PRETTYLINK = False

try:
    api.env.get_distribution('collective.z3cform.datagridfield')
    from collective.z3cform.datagridfield.datagridfield import DataGridField
    HAS_Z3CFORM_DATAGRIDFIELD = True
except pkg_resources.DistributionNotFound:
    HAS_Z3CFORM_DATAGRIDFIELD = False


EMPTY_STRING = '__empty_string__'
EMPTY_DATE = date(1950, 1, 1)


class BaseColumn(column.GetAttrColumn):

    implements(IFacetedColumn)

    sort_index = None
    # as we use setUpColumns, weight is 1 for every columns
    weight = 1
    # we can use a icon for header
    header_image = None
    # we can inject some javascript in the header
    header_js = None
    # header help message
    header_help = None
    # enable caching, needs to be implemented by Column
    use_caching = True
    # escape
    escape = True
    # get value from object instead brain?
    the_object = False

    def getValue(self, item):
        """ """
        if self.the_object:
            return safe_unicode(base_getattr(self._getObject(item), self.attrName))
        else:
            return super(BaseColumn, self).getValue(item)

    @property
    def cssClasses(self):
        """Generate a default CSS class for each <th> and <td> so we can skin it if necessary."""
        return {'th': 'th_header_{0}'.format(self.__name__),
                'td': 'td_cell_{0}'.format(self.__name__), }

    def getCSSClasses(self, item):
        return self.cssClasses

    def renderCell(self, item):
        return self.getValue(item) or u'-'

    def _getObject(self, item):
        """Caching for getObject."""
        itemUID = item.UID
        if not hasattr(self.table, '_v_cached_objects'):
            self.table._v_cached_objects = {}
        if itemUID not in self.table._v_cached_objects:
            self.table._v_cached_objects[itemUID] = item._unrestrictedGetObject()
        return self.table._v_cached_objects[itemUID]

    def _get_cached_result(self, value):
        if getattr(self, '_cached_result', None):
            if hasattr(value, '__iter__'):
                value = '_'.join(value)
            return self._cached_result.get(value, None)

    def _store_cached_result(self, value, result):
        """ """
        if getattr(self, '_cached_result', None) is None:
            self._cached_result = {}
        if hasattr(value, '__iter__'):
            value = '_'.join(value)
        self._cached_result[value] = result


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
        # include help message
        if self.column.header_help:
            header_help = translate(
                self.column.header_help,
                domain='collective.eeafaceted.z3ctable',
                context=self.request)
            header = u'<acronym title="{0}">{1}</acronym>'.format(
                header_help, header)
        # a column can specifically declare that it is not sortable
        # by setting sort_index to -1
        if not self.column.sort_index == -1:
            sort_on_name = self.table.sorting_criterion_name
            if sort_on_name and (self.column.sort_index or self.column.attrName):
                order_arrow = self.order_arrow
                faceted_url = self.faceted_url
                query_string = self.query_string
                if order_arrow:
                    query = self.table.query.get('sort_order', 'ascending')
                    contray_sort_order = (query == 'ascending' and 'descending' or 'ascending')
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
        """Take HTTP_REFERER as faceted page is done using a XHRequest we will have
           the real complete URL including ending '/' or '/view' and click on sorting
           will not redirect anymore."""
        return self.request.get('HTTP_REFERER') or '/'.join(self.request.get('URL').split('/')[:-1])

    @property
    def query_string(self):
        query = self.request_query
        sort_on_name = self.table.sorting_criterion_name

        if (self.table.query.get('sort_on', '') == self.sort_on or self.table.sortOn == self.column.id) and \
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


class AwakeObjectMethodColumn(BaseColumn):
    """Column that will wake the object then call attrName on it."""
    # column not sortable
    sort_index = -1
    params = {}
    weight = 40

    def renderCell(self, item):
        obj = self._getObject(item)
        try:
            return safe_unicode(base_getattr(obj, self.attrName)(**self.params)) or u'-'
        except TypeError:
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
    ignored_value = EMPTY_STRING

    def renderCell(self, item):
        value = self.getValue(item)
        if not value or value == self.ignored_value:
            return u'-'
        value = get_user_fullname(value)
        return safe_unicode(value)


class DateColumn(BaseColumn):
    """ """
    long_format = False
    time_only = False
    ignored_value = EMPTY_DATE
    # not necessary to escape, everything is generated
    escape = False

    def renderCell(self, item):
        value = self.getValue(item)
        if isinstance(value, DateTime):
            value = value.asdatetime().date()
        if not value or value == 'None' or value == self.ignored_value:
            return u'-'
        if self.use_caching:
            res = self._get_cached_result(value)
            if res:
                return res
        res = api.portal.get_localized_time(datetime=value, long_format=self.long_format, time_only=self.time_only)
        if self.use_caching:
            self._store_cached_result(value, res)
        return res


class I18nColumn(BaseColumn):
    """GetAttrColumn which translates its content."""

    i18n_domain = 'plone'
    msgid_prefix = ''
    weight = 30

    def renderCell(self, item):
        value = self.getValue(item)
        if value == self.defaultValue:
            return u'-'
        # make sure msgid is unicode in case it contains special characters
        msgid = safe_unicode("{0}{1}".format(self.msgid_prefix, value))
        return translate(msgid,
                         domain=self.i18n_domain,
                         context=self.request)


class BooleanColumn(I18nColumn):
    """ """

    i18n_domain = 'collective.eeafaceted.z3ctable'
    msgid_prefix = 'boolean_value_'

    def getCSSClasses(self, item):
        cssClasses = self.cssClasses
        cssClasses['td'] = cssClasses['td'] + ' bool_value_{0}'.format(
            str(self.getValue(item)).lower())
        return cssClasses


class BrowserViewCallColumn(BaseColumn):
    """A column that display the result of a given browser view name call."""
    # column not sortable
    sort_index = -1
    params = {}
    view_name = None

    def renderCell(self, item):
        if not self.view_name:
            raise KeyError('A "view_name" must be defined for column "{0}" !'.format(self.attrName))

        # avoid double '//' that breaks (un)restrictedTraverse, moreover path can not be unicode
        path = os.path.join(item.getPath(), self.view_name).encode('utf-8')
        return self.table.portal.unrestrictedTraverse(path)(**self.params)


class VocabularyColumn(BaseColumn):
    """A column that is aware of a vocabulary and that will get value to display from it."""

    # named utility
    vocabulary = None
    ignored_value = EMPTY_STRING
    # we manage escape here manually
    escape = False

    def renderCell(self, item):
        value = self.getValue(item)
        if not value or value == self.ignored_value:
            return u'-'

        # caching when several same values in same column
        if self.use_caching:
            res = self._get_cached_result(value)
            if res:
                return res

        # the vocabulary instance is cached
        if not hasattr(self, '_cached_vocab_instance'):
            if not self.vocabulary:
                raise KeyError('A "vocabulary" must be defined for column "{0}" !'.format(
                    self.attrName))
            factory = queryUtility(IVocabularyFactory, self.vocabulary)
            if not factory:
                raise KeyError('The vocabulary "{0}" used for column "{1}" was not found !'.format(
                    self.vocabulary, self.attrName))

            self._cached_vocab_instance = factory(self.context)

        # make sure we have an iterable
        if not hasattr(value, '__iter__'):
            value = [value]
        res = []
        for v in value:
            try:
                res.append(html.escape(safe_unicode(self._cached_vocab_instance.getTerm(v).title)))
            except LookupError:
                # in case an element is not in the vocabulary, add the value
                res.append(safe_unicode(v))
        res = ', '.join(res)
        if self.use_caching:
            self._store_cached_result(value, res)
        return res


class AbbrColumn(VocabularyColumn):
    """A column that will display a <abbr> HTML tag and that will show a full version on hover.
       It is aware of 2 vocabularies, one to manage abbreviation and one to manage full value."""

    # named utility
    full_vocabulary = None
    separator = u', '
    # we manage escape here manually
    escape = False

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            return u'-'

        # caching when several same values in same column
        if self.use_caching:
            res = self._get_cached_result(value)
            if res:
                return res

        # the vocabulary instances are cached
        if not hasattr(self, '_cached_full_vocab_instance'):
            if not self.vocabulary or not self.full_vocabulary:
                raise KeyError(
                    'A "vocabulary" and a "full_vocabulary" must be defined for column "{0}" !'.format(self.attrName))
            acronym_factory = queryUtility(IVocabularyFactory, self.vocabulary)
            if not acronym_factory:
                raise KeyError(
                    'The vocabulary "{0}" used for column "{1}" was not found !'.format(self.vocabulary,
                                                                                        self.attrName))
            full_factory = queryUtility(IVocabularyFactory, self.full_vocabulary)
            if not full_factory:
                raise KeyError(
                    'The vocabulary "{0}" used for column "{1}" was not found !'.format(self.full_vocabulary,
                                                                                        self.attrName))
            self._cached_acronym_vocab_instance = acronym_factory(self.context)
            self._cached_full_vocab_instance = full_factory(self.context)

        # make sure we have an iterable
        if not hasattr(value, '__iter__'):
            value = [value]
        res = []
        for v in value:
            try:
                tag_title = self._cached_full_vocab_instance.getTerm(v).title
                tag_title = tag_title.replace("'", "&#39;")
                res.append(u"<abbr title='{0}'>{1}</abbr>".format(
                    html.escape(safe_unicode(tag_title)),
                    html.escape(safe_unicode(self._cached_acronym_vocab_instance.getTerm(v).title))))
            except LookupError:
                # in case an element is not in the vocabulary, add the value
                tag_title = html.escape(safe_unicode(v))
                res.append(u"<abbr title='{0}'>{1}</abbr>".format(tag_title, tag_title))
        # manage separator without "join" to move the separator inside the <abbr></abbr>
        res = [v.replace('</abbr>', self.separator + '</abbr>') for v in res[:-1]] + res[-1:]
        res = ''.join(res)
        if self.use_caching:
            self._store_cached_result(value, res)
        return res


class ColorColumn(I18nColumn):
    """A column that is aimed to display a background color
       and a help message on hover."""

    # no real color is applied but a generated CSS class
    cssClassPrefix = 'column'
    # Hide the head cell but fill it with spaces so it does
    # not shrink to nothing if table is too large
    header = u'&nbsp;&nbsp;&nbsp;'
    # we manage escape here manually
    escape = False

    def renderCell(self, item):
        """Display a message."""
        translated_msg = super(ColorColumn, self).renderCell(item)
        return u'<div title="{0}">&nbsp;</div>'.format(html.escape(translated_msg))

    def getCSSClasses(self, item):
        """Generate a CSS class to apply on the TD depending on the value."""
        return {'td': "{0}_{1}_{2}".format(self.cssClassPrefix,
                                           str(self.attrName),
                                           html.escape(self.getValue(item)))}


class CheckBoxColumn(BaseColumn):
    """
      Display a checkbox.
    """

    name = 'select_item'
    checked_by_default = True
    attrName = 'UID'
    weight = 100
    # not necessary to escape, everything is generated
    escape = False

    def renderHeadCell(self):
        """ """
        title = translate('select_unselect_items',
                          domain='collective.eeafaceted.z3ctable',
                          context=self.request,
                          default="Select/unselect all")
        return u'<input type="checkbox" id="select_unselect_items" onClick="toggleCheckboxes(this, \'{0}\')" ' \
               u'title="{1}" name="{0}" {2}/>'.format(
                   self.name, title, self.checked_by_default and "checked " or "")

    def renderCell(self, item):
        """ """
        return u'<label class="select-item-label"><input type="checkbox" name="%s" value="%s" %s/></label>' \
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


class ElementNumberColumn(BaseColumn):
    header = u''
    # not necessary to escape, everything is generated
    escape = False

    def renderCell(self, item):
        """ """
        start = 1
        # if we have a batch, use it
        if base_hasattr(self.table, 'batch'):
            start = self.table.batch.start
            values_from = start - 1
            values_to = values_from + self.table.batch.length
            values_uids = [v.UID for v in self.table.values._sequence[
                values_from:values_to]]
        else:
            # this column may also be used with more classical z3c.table
            # where there is no batch and we display the entire table
            values_uids = [v.UID for v in self.table.values]
        return start + values_uids.index(item.UID)


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

    header = _('header_Title')
    sort_index = 'sortable_title'
    weight = 0
    # we manage escape here manually
    escape = False

    def renderCell(self, item):
        value = self.getValue(item)
        if not value:
            value = u'-'
        value = safe_unicode(value)
        return u'<a href="{0}">{1}</a>'.format(item.getURL(), html.escape(value))


class PrettyLinkColumn(TitleColumn):
    """A column that displays the IPrettyLink.getLink column.
       This rely on imio.prettylink."""

    # escape is managed by imio.prettylink
    escape = False

    params = {}

    @property
    def cssClasses(self):
        """Generate a CSS class for each <th> so we can skin it if necessary."""
        cssClasses = super(PrettyLinkColumn, self).cssClasses.copy() or {}
        cssClasses.update({'td': 'pretty_link', })
        return cssClasses

    def contentValue(self, item):
        """ """
        return None

    def getPrettyLink(self, obj):
        pl = IPrettyLink(obj)
        for k, v in self.params.items():
            setattr(pl, k, v)
        pl.contentValue = self.contentValue(obj)
        return pl.getLink()

    def renderCell(self, item):
        """ """
        return self.getPrettyLink(self._getObject(item))


class PrettyLinkWithAdditionalInfosColumn(PrettyLinkColumn):
    """A column that displays the PrettyLinkColumn column
       and includes additional informations.
       This only works when used with DX content types."""

    # additional infos config
    ai_widget_render_pattern = u'<div class="discreet {2} {3}">' \
        u'<label class="horizontal">{0}</label>\n<div class="{4}">{1}</div></div>'
    # "*" means every non empty fields
    ai_included_fields = "*"
    ai_excluded_fields = []
    ai_extra_fields = ['id', 'UID', 'description']
    # as we use caching, we avoid widget.update except if field name found here
    ai_reloaded_fields = []
    ai_highlighted_fields = []
    ai_highligh_css_class = "highlight"
    ai_generate_css_class_fields = []
    simplified_datagridfield = False

    def _field_css_class(self, widget):
        """Compute a field CSS class based on field name and value."""
        field_css_class = ''
        if widget.__name__ in self.ai_generate_css_class_fields:
            field_css_class = '{0}_{1}'.format(
                widget.__name__, str(widget.field.get(widget.context)).lower())
        return field_css_class

    def additional_infos(self, item):
        """ """
        res = u'<div class="additional-infos">'
        # caching
        obj = self._getObject(item)
        # Manage ai_extra_fields
        for extra_field in self.ai_extra_fields:
            if base_hasattr(obj, extra_field):
                value = getattr(obj, extra_field)
                if callable(value):
                    value = value()
                if value:
                    res += u'<div class="discreet"><label class="horizontal">{0}</label>' \
                        '<div class="type-textarea-widget">{1}</div></div>'.format(extra_field.capitalize(), value)
        if not self.use_caching or getattr(self, '_cached_view', None) is None:
            view = obj.restrictedTraverse('view')
            self._cached_view = view
            view.update()
            # handle widgets
            widgets = view.widgets.values()
            for group in view.groups:
                widgets.extend(group.widgets.values())
        else:
            view = self._cached_view
            view.context = obj
            for widget in view.widgets.values():
                widget.context = view.context
                dm = getMultiAdapter((view.context, widget.field), IDataManager)
                value = dm.get()
                if value:
                    # special management for RelationField
                    # avoid to update widget when not necessary
                    if isinstance(widget.field, (RelationChoice, RelationList)) or \
                       widget.field.__name__ in self.ai_reloaded_fields:
                        if widget.field.__name__ in self.ai_reloaded_fields:
                            widget.terms = None
                        widget.update()

                    if self.simplified_datagridfield and \
                       HAS_Z3CFORM_DATAGRIDFIELD and \
                       isinstance(widget, DataGridField):
                        widget._value = value
                    else:
                        converter = IDataConverter(widget)
                        converted = converter.toWidgetValue(value)
                        # special behavior for datagridfield where setting the value
                        # will updateWidgets and is slow/slow/slow...
                        widget.value = converted
                else:
                    widget.value = None
            widgets = view.widgets.values()
        for widget in widgets:
            if widget.__name__ not in self.ai_excluded_fields and \
               (self.ai_included_fields == "*" or widget.__name__ in self.ai_included_fields) and \
               widget.value not in (None, '', '--NOVALUE--', u'', (), [], (''), [''], ['--NOVALUE--']):
                widget_name = widget.__name__
                css_class = widget_name in self.ai_highlighted_fields and self.ai_highligh_css_class or ''
                field_css_class = self._field_css_class(widget)
                translated_label = translate(widget.label, context=self.request)
                # render the widget
                if self.simplified_datagridfield and \
                   HAS_Z3CFORM_DATAGRIDFIELD and \
                   isinstance(widget, DataGridField):
                    _rendered_value = self._render_datagridfield(view, widget)
                else:
                    _rendered_value = widget.render()
                field_type_css_class = "type-{0}".format(widget.klass.split(' ')[0])
                res += self.ai_widget_render_pattern.format(
                    translated_label, _rendered_value, css_class, field_css_class, field_type_css_class)
        res += "</div>"
        return res

    def _render_datagridfield(self, view, widget):
        '''Datagridfield is so slow to render we can not use widget rendering,
           we will use a collective.excelexport exportable to render it.'''
        exportable = get_exportable_for_fieldname(view.context, widget.__name__, self.request)
        _rendered_value = exportable.render_value(view.context)
        # format exportable value
        _rendered_value = u'<div class="table-col-datagrid-header">{0}'.format(_rendered_value)
        _rendered_value = _rendered_value.replace(
            ' : ', ' :&nbsp;</div><div class="table-col-datagrid-value">')
        # end of row
        _rendered_value = _rendered_value.replace(
            '\n', '</div><br/><br/><div class="table-col-datagrid-header">')
        _rendered_value = _rendered_value.replace(
            ' / ', '</div><br/><div class="table-col-datagrid-header">')
        _rendered_value = u'{0}</div>'.format(_rendered_value)
        return _rendered_value

    def renderCell(self, item):
        """ """
        rendered_cell = super(PrettyLinkWithAdditionalInfosColumn, self).renderCell(item)
        return rendered_cell + self.additional_infos(item)


class RelationPrettyLinkColumn(RelationTitleColumn, PrettyLinkColumn):
    """
    A column displaying related items with IPrettyLink.getLink
    """

    params = {}

    def target_display(self, obj):
        return PrettyLinkColumn.getPrettyLink(self, obj)


class ActionsColumn(BrowserViewCallColumn):
    """
    A column displaying available actions of the listed item.
    This rely on imio.actionspanel.
    """

    header_js = '<script type="text/javascript">jQuery(document).ready(initializeOverlays);' \
                'jQuery(document).ready(preventDefaultClick);</script>'
    view_name = 'actions_panel'
    params = {'showHistory': True, 'showActions': True}
    # not necessary to escape, everything is generated
    escape = False


class IconsColumn(BaseColumn):
    """
        Column displaying icons with title tag
    """
    attrName = None
    defaultValue = []  # default value for self.getValue()
    separator = ' '

    def values(self, item):
        return self.getValue(item)

    def titleValue(self, item, val):
        return val

    def classValue(self, item, val):
        return ''

    def srcValue(self, item, val):
        return '{}/{}'.format(self.table.portal_url, val)

    def renderCell(self, item):
        tags = []
        for val in self.values(item) or []:
            tag = u"""<img title="{}" class="{}" src="{}" />""".format(self.titleValue(item, val),
                                                                       self.classValue(item, val),
                                                                       self.srcValue(item, val))
            tags.append(tag)
        return self.separator.join(tags)
