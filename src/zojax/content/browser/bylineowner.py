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
from zope.traversing.browser import absoluteURL
from zojax.ownership.interfaces import IOwnership
from zojax.principal.profile.interfaces import IPersonalProfile


class ContentOwner(object):

    def update(self):
        context = self.context
        request = self.request

        principal = None

        ownership = IOwnership(context, None)
        if ownership is not None:
            principal = ownership.owner

        profile = IPersonalProfile(principal, None)
        if profile is not None:
            self.owner = profile.title

            space = profile.space
            if space is not None:
                self.profile = '%s/'%absoluteURL(space, request)

    def isAvailable(self):
        return True
