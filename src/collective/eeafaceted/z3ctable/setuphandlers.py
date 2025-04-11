# -*- coding: utf-8 -*-


def isNotCurrentProfile(context):
    return context.readDataFile("collectiveeeafacetedz3ctable_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

def uninstall(context):
    pass
