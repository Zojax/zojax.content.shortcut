##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zojax.content.type.constraints import checkObject
"""

$Id$
"""
from zope.security.tests.test_standard_checkers import check_forbidden_call
from zope.security.checker import canAccess
from zope.proxy import getProxiedObject, non_overridable
from zope import component, interface
from zc.shortcut.interfaces import IObjectLinker, IShortcut
from zc.shortcut.factory import Factory
from zc.shortcut.shortcut import Shortcut
from zc.shortcut.proxy import TargetProxy, ProxyBase
from zc.shortcut.adapters import ObjectLinkerAdapter
from z3c.proxy.container import ContainerLocationProxy, proxify
from zope.security.proxy import removeSecurityProxy
from zope.proxy import removeAllProxies, sameProxiedObjects
from zope.app.intid.interfaces import IIntIdAddedEvent, IIntIdRemovedEvent,\
    IIntIds, IIntIdsManage
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zojax.members.interfaces import IMembersAware

from zojax.content.type.interfaces import IContentContainer, IContentType, IItem,\
    IContent, ISearchableContent
from zojax.ownership.interfaces import IOwnership
from zojax.catalog.generations.install import findObjectsMatching
from zojax.catalog.utils import indexObject
from interfaces import IShortcuts


def target(self):
    target = self.raw_target
    proxied_target = TargetProxy(target, target.__parent__, target.__name__, self)
    if IContentContainer.providedBy(target):
        return ContainerLocationProxy(proxied_target, self.__parent__, self.__name__)
    return proxied_target

def members(self):
    return self.target.members

Shortcut.target = property(target)
Shortcut.members = property(members)

@component.adapter(IShortcut)
@interface.implementer(IContentType)
def getShortcutContentType(context):
    return IContentType(context.target, None)

@component.adapter(IShortcut)
@interface.implementer(IItem)
def getShortcutItem(context):
    return IItem(context.target, None)

@component.adapter(IShortcut)
def getShortcutItemBlogPost(context):
    from zojax.blogger.interfaces import IBlogPost
    return IBlogPost(context.target, None)

@component.adapter(IShortcut)
@interface.implementer(IOwnership)
def getShortcutOwnership(context):
    return IOwnership(context.target, None)


class ShortcutsExtension(object):

    def add(self, ob):
        id = component.getUtility(IIntIds).getId(ob)
        items = self.data.get('items', set())
        items.add(id)
        self.data['items'] = items

    def remove(self, ob):
        id = component.getUtility(IIntIds).getId(ob)
        items = self.data.get('items', set())
        try:
            items.remove(id)
        except KeyError:
            pass
        self.data['items'] = items

    def items(self):
        ids = component.getUtility(IIntIds)
        try:
            return filter(bool, map(ids.queryObject, self.data.get('items', set())))
        except TypeError:
            return ()

def safeIndexObject(item):
    try:
        indexObject(item)
    except KeyError:
        return


@component.adapter(IShortcut, IIntIdAddedEvent)
def shortCutAdded(object, obevent):
    ext = IShortcuts(object.raw_target, None)
    if ext is not None:
        ext.add(object)
        map(lambda x: safeIndexObject(x), findObjectsMatching(object.raw_target, ISearchableContent.providedBy))


@component.adapter(IShortcut, IIntIdRemovedEvent)
def shortCutRemoved(object, event):
    ext = IShortcuts(object.raw_target, None)
    if ext is not None:
        ext.remove(object)
        map(lambda x: safeIndexObject(x), findObjectsMatching(object.raw_target, ISearchableContent.providedBy))


@component.adapter(IShortcut, IObjectModifiedEvent)
def shortCutModified(object, event):
    pass


@component.adapter(IContent, IIntIdRemovedEvent)
def objectRemoved(object, event):
    for shortcut in list(IShortcuts(object, {}).items()):
        del shortcut.__parent__[shortcut.__name__]


class ContentLinker(ObjectLinkerAdapter):
    component.adapts(IContent)
    interface.implements(IObjectLinker)

    def linkableTo(self, target, name=None):
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self.context)
        except interface.Invalid:
            return False
        return True
