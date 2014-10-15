# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from collective.z3ctable.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.z3ctable into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.z3ctable is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.z3ctable'))

    def test_uninstall(self):
        """Test if collective.z3ctable is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.z3ctable'])
        self.assertFalse(self.installer.isProductInstalled('collective.z3ctable'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveZ3ctableLayer is registered."""
        from collective.z3ctable.interfaces import ICollectiveZ3ctableLayer
        from plone.browserlayer import utils
        self.failUnless(ICollectiveZ3ctableLayer in utils.registered_layers())
