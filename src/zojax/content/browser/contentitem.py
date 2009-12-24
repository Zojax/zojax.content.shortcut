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
from interfaces import _
from zojax.content.type.interfaces import IItem


class ContentItem(object):

    title = u''
    description = u''

    def update(self):
        super(ContentItem, self).update()

        item = IItem(self.context, None)
        if item is not None:
            self.title = item.title or _('[No title]')
            self.description = item.description
        self.item = item

    def isAvailable(self):
        return self.item is not None
