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
from zope import interface, component
from zojax.layoutform import Fields, PageletAddForm
from zojax.content.type.interfaces import IContentViewView

from content import IContent2, Content2


class AddContent2(PageletAddForm):

    fields = Fields(IContent2)
    label = u'Custom Add Form for Content 2'

    def create(self, data):
        return Content2(data['title'], data['description'])

    def add(self, content):
        self.context.add(content)


class ContentViewView(object):
    interface.implements(IContentViewView)
    component.adapts(IContent2, interface.Interface)

    name = 'index.html'

    def __init__(self, content, request):
        pass
