# -*- coding: utf-8 -*-

""" Sorting form aware widget"""

from eea.facetednavigation.widgets.sorting.widget import Widget
from eea.facetednavigation.widgets.sorting.interfaces import ISortingSchema


class ISortingFormAwareSchema(ISortingSchema):
    """ """


class SortingFormAwareAbstractWidget(Widget):
    """ Override the sorting widget so it can handle sorting data from the form.
        By default, if the sorting criteria is hidden, it is not possible to use sorting,
        it will only sort using the default sorting method defined.  Here if we pass
        relevant data in the form (widget id and value), it works.  This is made so header columns
        can use sorting.
    """

    def query(self, form):
        """ Get value from form and return a catalog dict query
        """
        query = {}

        # XXX changed by collective.eeafaceted.z3ctable
        # added the ' and not self.data.getId() in form' part
        if self.hidden and not self.data.getId() in form:
            default = self.default
            sort_on = len(default) > 0 and default[0] or None
            reverse = len(default) > 1 and default[1] or False
            # XXX changed by collective.eeafaceted.z3ctable
            # save info in the request.form so method query
            # of collectionwidget may use it and not add
            # the sort_on from the collection
            if sort_on:
                self.request.form[self.data.__name__ + '[]'] = sort_on
                self.request.form['reversed'] = reverse
        else:
            sort_on = form.get(self.data.getId(), '')
            reverse = form.get('reversed', False)

        if sort_on:
            query['sort_on'] = sort_on

        if reverse:
            query['sort_order'] = 'descending'
        else:
            query['sort_order'] = 'ascending'

        return query
