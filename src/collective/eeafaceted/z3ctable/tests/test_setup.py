# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.testing import NAKED_PLONE_INTEGRATION

from plone import api
from plone.app.testing import applyProfile

import unittest


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.z3ctable into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.eeafaceted.z3ctable is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.eeafaceted.z3ctable'))

    def test_uninstall(self):
        """Test if collective.collective.eeafaceted.z3ctable is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.eeafaceted.z3ctable'])
        self.assertFalse(self.installer.isProductInstalled('collective.eeafaceted.z3ctable'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveZ3ctableLayer is registered."""
        from collective.eeafaceted.z3ctable.interfaces import ICollectiveEeafacetedZ3ctableLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveEeafacetedZ3ctableLayer in utils.registered_layers())


class TestInstallDependencies(unittest.TestCase):

    layer = NAKED_PLONE_INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_eeafacetednavigation_is_dependency_of_eeaz3ctable(self):
        """
        eea.facetednavigation should be installed when we install eeafaceted.z3ctable
        """
        self.assertTrue(not self.installer.isProductInstalled('eea.facetednavigation'))
        applyProfile(self.portal, 'collective.eeafaceted.z3ctable:testing')
        self.assertTrue(self.installer.isProductInstalled('eea.facetednavigation'))
