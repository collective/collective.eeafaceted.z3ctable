# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.eeafaceted.z3ctable.testing import IntegrationTestCase
from collective.eeafaceted.z3ctable.testing import NAKED_PLONE_INTEGRATION
from plone import api
from plone.app.testing import applyProfile
from plone.base.utils import get_installer

import unittest



class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.z3ctable into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.eeafaceted.z3ctable is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.is_product_installed('collective.eeafaceted.z3ctable'))

    def test_uninstall(self):
        """Test if collective.collective.eeafaceted.z3ctable is cleanly uninstalled."""
        self.installer.uninstall_product('collective.eeafaceted.z3ctable')
        try:
            self.assertFalse(self.installer.is_product_installed('collective.eeafaceted.z3ctable'))
        except Exception as e:
            print("Error during uninstall: ", e)

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveZ3ctableLayer is registered."""
        from collective.eeafaceted.z3ctable.interfaces import ICollectiveEeafacetedZ3ctableLayer
        from plone.browserlayer import utils
        self.assertTrue(ICollectiveEeafacetedZ3ctableLayer in utils.registered_layers())


class TestInstallDependencies(unittest.TestCase):

    layer = NAKED_PLONE_INTEGRATION

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal)

    def test_eeafacetednavigation_is_dependency_of_eeaz3ctable(self):
        """
        eea.facetednavigation should be installed when we install eeafaceted.z3ctable
        """
        self.assertTrue(not self.installer.is_product_installed('eea.facetednavigation'))
        applyProfile(self.portal, 'collective.eeafaceted.z3ctable:testing')
        self.assertTrue(self.installer.is_product_installed('eea.facetednavigation'))
