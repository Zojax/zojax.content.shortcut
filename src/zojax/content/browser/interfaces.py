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
from zope.i18nmessageid import MessageFactory
from zojax.pageelement.interfaces import IPageElement

_ = MessageFactory('zojax.content.browser')


class IContentContext(interface.Interface):
    """ Content context """


class IContentAdding(interface.Interface):
    """ Content adding """

    def getContentType(name):
        """ return bound content type object """


class IContentTitle(IPageElement):
    """ title """


class IContentByline(IPageElement):
    """ header """


class IContentDescription(IPageElement):
    """ description """


class IContentFooter(IPageElement):
    """ footer """


class IContentBottom(IPageElement):
    """ bottom """


class IContainerListing(interface.Interface):
    """ container listing """


class IRenameContainerContents(interface.Interface):
    """ rename container contents table """


class IContainerURL(interface.Interface):
    """ container item custom url generation """

    def absoluteURL():
        """ item absolute url """


# edit content wizard step

class IContentsStep(interface.Interface):
    """ contents step """
