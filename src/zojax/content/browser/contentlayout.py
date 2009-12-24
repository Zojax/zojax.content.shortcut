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
from zojax.content.type.interfaces import IContent, IContentType


class ContentViewLayout(object):

    klass = u''

    def update(self):
        context = self.context
        while not IContent.providedBy(context):
            context = getattr(context, '__parent__', None)
            if context is None:
                break

        if context is not None:
            ct = IContentType(context, None)
            if ct is not None:
                self.klass = ct.name.replace('.', '-')

        super(ContentViewLayout, self).update()
