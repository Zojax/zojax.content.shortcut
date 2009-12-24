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
""" custom IBreadcrumb implementation for IConfiglet

$Id$
"""
from zope import component, interface
from zope.component import queryMultiAdapter
from zope.traversing.browser import absoluteURL
from z3c.breadcrumb.browser import GenericBreadcrumb
from zojax.content.type.interfaces import IItem, IContent
from zojax.content.type.interfaces import IContentViewView


class ContentBreadcrumb(GenericBreadcrumb):
    """
    >>> from zope import interface
    >>> from zojax.content.type.testing import setUpContents
    >>> from zojax.content.type.item import Item
    >>> from zojax.content.type.interfaces import IContent
    >>> setUpContents()

    >>> class Content(Item):
    ...     interface.implements(IContent)

    >>> content = Content('Content')

    >>> crumb = ContentBreadcrumb(content, None)
    >>> crumb.name
    u'Content'

    >>> class Content(object):
    ...     pass

    >>> content = Content()
    >>> content.title = u'Content'

    >>> crumb = ContentBreadcrumb(content, None)
    >>> crumb.name
    u'Content'

    >>> content.title = ''
    >>> content.__name__ = u'content'
    >>> crumb.name
    u'content'
    """
    component.adapts(IContent, interface.Interface)

    @property
    def name(self):
        item = IItem(self.context, None)
        if item is not None:
            return item.title or self.context.__name__
        else:
            name = getattr(self.context, 'title', '')
            if not name:
                name = self.context.__name__
            return name

    @property
    def url(self):
        viewName = queryMultiAdapter(
            (self.context, self.request), IContentViewView)
        if viewName is not None:
            return '%s/%s'%(
                absoluteURL(self.context, self.request), viewName.name)
        else:
            return '%s/'%(absoluteURL(self.context, self.request))
