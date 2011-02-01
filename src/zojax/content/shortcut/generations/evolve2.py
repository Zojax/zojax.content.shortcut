##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################from zope.app.container.contained import ObjectAddedEvent
"""

$Id$
"""
from zope import interface, component
from zope.app.component.interfaces import ISite
from zope.app.zopeappgenerations import getRootFolder
from zope.app.component.hooks import getSite, setSite
from zope.component.interfaces import ComponentLookupError
from zope.traversing.api import getParents

from zc.shortcut.interfaces import IShortcut

from zojax.content.shortcut.shortcut import shortCutAdded, objectRemoved


def evolve(context):
    root = getRootFolder(context)
    old_site = getSite()
    for site in findObjectsMatching(root, ISite.providedBy):
        setSite(site)
        try:
            for shortcut in list(findObjectsMatching(site, IShortcut.providedBy)):
                print 'updating shortcut', shortcut
                try:
                    getParents(shortcut.raw_target)
                except TypeError:
                    objectRemoved(shortcut.raw_target, None) 
        finally:
            setSite(old_site)


def findObjectsMatching(root, condition):
    if condition(root):
        yield root

    if hasattr(root, 'values') and callable(root.values):
        for subobj in root.values():
            for match in findObjectsMatching(subobj, condition):
                yield match
