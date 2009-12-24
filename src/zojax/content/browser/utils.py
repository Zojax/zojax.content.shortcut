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
from zojax.content.type.interfaces import IContentType, IContentContainer


def findContainer(context):
    """
    >>> from zope import interface
    >>> from zojax.content.browser.utils import findContainer

    >>> class Content(object):
    ...     __parent__ = None

    >>> class Container(object):
    ...     interface.implements(IContentContainer)
    ...     __parent__ = None

    >>> ob = Content()
    >>> ob.__parent__ = Content()
    >>> ob.__parent__.__parent__ = Content()

    No root container

    >>> findContainer(ob) is None
    True

    Recursive

    >>> ob.__parent__.__parent__.__parent__ = ob.__parent__.__parent__
    >>> findContainer(ob) is None
    True

    With container

    >>> ob.__parent__.__parent__.__parent__ = Container()

    >>> print findContainer(ob)
    <zojax.content.browser.utils.Container object at ...>
    """
    parent = context

    seen = set()

    while True:
        if parent in seen:
            break

        seen.add(parent)

        if IContentContainer.providedBy(parent):
            return parent

        parent = getattr(parent, '__parent__', None)
        if parent is None:
            break

    return None
