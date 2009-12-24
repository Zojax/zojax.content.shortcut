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
"""

$Id$
"""
from zope import interface
from zope.proxy import sameProxiedObjects
from zope.security import checkPermission
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.traversing.browser import absoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.contentprovider.interfaces import IContentProvider

from zojax.wizard.step import WizardStep
from zojax.layout.interfaces import IPagelet
from zojax.content.type.interfaces import \
    IItem, IOrder, IContentType, IContentViewView, IContentContainer

from interfaces import _, IContainerListing, IContentsStep


class Contents(object):

    def update(self):
        super(Contents, self).update()

        item = IItem(self.context, None)
        if item is not None:
            self.content_title = item.title or self.context.__name__
            self.content_description = item.description
        else:
            dc = IDCDescriptiveProperties(self.context, None)
            if dc is not None:
                self.content_title = dc.title
                self.content_description = dc.description

        contenttype = IContentType(self.context, None)
        try:
            contenttype.listContainedTypes().next()
            self.hasAdding = True
        except:
            self.hasAdding = False

    def upperContainer(self):
        request = self.request
        vhr = request.getVirtualHostRoot()
        parent = getattr(self.context, '__parent__', None)

        while True:
            if (parent is None or
                sameProxiedObjects(parent, vhr) or
                IContainmentRoot.providedBy(parent)):
                return None

            if IContentContainer.providedBy(parent):
                url = absoluteURL(parent, request)

                if checkPermission('zojax.ModifyContent', parent):
                    return '%s/@@context.html'%url

                viewName = queryMultiAdapter((parent, request), IContentViewView)
                if viewName:
                    return '%s/%s'%(url, viewName.name)

                return '%s/'%url
            else:
                parent = getattr(parent, '__parent__', None)


class ContentsStep(Contents, WizardStep):
    interface.implements(IContentsStep)

    permission = 'zojax.ModifyContent'


class Listing(object):

    def update(self):
        super(Listing, self).update()

        self.table = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='content.container.listing')
        self.table.update()

    def render(self):
        return self.table.render()

    def __call__(self, *args, **kw):
        if 'index.html' in self.context:
            view = queryMultiAdapter(
                (self.context['index.html'], self.request), IPagelet)
            if view is not None:
                return view()

        return super(Listing, self).__call__()


class RebuildOrder(object):

    def __call__(self):
        order = IOrder(self.context, None)
        if order is not None:
            order.rebuild()

        self.request.response.redirect('context.html')
