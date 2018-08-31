# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from eea.facetednavigation.layout.interfaces import IFacetedLayout
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList

from plone import api
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.supermodel import model
from plone.testing import z2

import collective.eeafaceted.z3ctable

import unittest


class ITestingType(model.Schema):

    afield = schema.TextLine(
        title=u'A field',
        required=False
    )

    bool_field = schema.Bool(
        title=u'Boolean field',
        required=False,
        default=True
    )

    rel_item = RelationChoice(
        title=u"Rel item",
        source=ObjPathSourceBinder(),
        required=False,
    )

    rel_items = RelationList(
        title=u"Related Items",
        default=[],
        value_type=RelationChoice(title=u"Related", source=ObjPathSourceBinder()),
        required=False,
    )


class NakedPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ('collective.eeafaceted.z3ctable', 'eea.facetednavigation')

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.z3ctable,
                      name='testing.zcml')
        for p in self.products:
            z2.installProduct(app, p)

    def tearDownZope(self, app):
        """Tear down Zope."""
        z2.uninstallProduct(app, 'collective.eeafaceted.z3ctable')

NAKED_PLONE_FIXTURE = NakedPloneLayer(
    name="NAKED_PLONE_FIXTURE"
)

NAKED_PLONE_INTEGRATION = IntegrationTesting(
    bases=(NAKED_PLONE_FIXTURE,),
    name="NAKED_PLONE_INTEGRATION"
)


class CollectiveEeafacetedZ3ctableLayer(NakedPloneLayer):

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.eeafaceted.z3ctable:testing')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        eea_folder = api.content.create(
            type='Folder',
            id='eea_folder',
            title='EEA Folder',
            container=portal
        )
        eea_folder.reindexObject()

        eea_folder.restrictedTraverse('@@faceted_subtyper').enable()
        IFacetedLayout(eea_folder).update_layout('faceted-table-items')

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()


FIXTURE = CollectiveEeafacetedZ3ctableLayer(
    name="FIXTURE"
)


INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)


FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


ACCEPTANCE = FunctionalTesting(bases=(FIXTURE,
                                      REMOTE_LIBRARY_BUNDLE_FIXTURE,
                                      z2.ZSERVER_FIXTURE),
                               name="ACCEPTANCE")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.eea_folder = self.portal.get('eea_folder')
        self.faceted_z3ctable_view = self.eea_folder.restrictedTraverse('faceted-table-view')


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
