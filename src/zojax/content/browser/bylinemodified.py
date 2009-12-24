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
from zope.dublincore.interfaces import ICMFDublinCore
from zojax.formatter.utils import getFormatter


class ContentModified(object):

    def update(self):
        dc = ICMFDublinCore(self.context, None)

        if dc is not None and dc.modified:
            formatter = getFormatter(self.request, 'fancyDatetime', 'medium')
            self.modified = formatter.format(dc.modified)
        else:
            self.modified = None

    def isAvailable(self):
        return self.modified is not None
