# -*- coding: utf-8 -*-

# Copied from imio.helpers to prevent hard dependency
from plone import api
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode


def base_getattr(obj, attr_name, default=None):
    """ """
    if base_hasattr(obj, attr_name):
        return getattr(obj, attr_name, default)
    else:
        return default


def get_user_fullname(userid, none_if_no_user=False, none_if_unfound=False, with_user_id=False):
    """Get fullname without using getMemberInfo that is slow slow slow...
    We get it only from mutable_properties or authentic.

    :param userid: principal id
    :param none_if_no_user: return None if principal is not a user
    :param none_if_unfound: return None if principal is not found
    :param with_user_id: include user_id between () in the returned result
    :return: fullname or userid if fullname is empty.
    """
    userid = safe_unicode(userid)
    acl_users = api.portal.get_tool('acl_users')
    storages = [acl_users.mutable_properties._storage, ]
    # if authentic is available check it first
    if base_hasattr(acl_users, 'authentic'):
        storages.insert(0, acl_users.authentic._useridentities_by_userid)

    for storage in storages:
        data = storage.get(userid, None)  # do not find a ldap user with a space in it !
        if data is not None:
            fullname = u""
            # mutable_properties
            if hasattr(data, 'get'):
                if not data.get('isGroup'):
                    fullname = data.get('fullname')
                elif none_if_no_user:
                    return None
                else:
                    return userid
            # authentic
            else:
                fullname = data._identities['authentic-agents'].data['fullname']
            break
    else:  # we didn't find this userid
        if none_if_unfound:
            return None
        return userid
    # finally if fullname was not found, use getMemberInfo
    # this is necessary sometimes when using LDAP
    if not fullname:
        mt = api.portal.get_tool('portal_membership')
        info = mt.getMemberInfo(userid)
        if info:
            fullname = info.get('fullname', '')
    fullname = safe_unicode(fullname) or userid
    if with_user_id:
        fullname = u'{0} ({1})'.format(fullname, userid)
    return fullname

