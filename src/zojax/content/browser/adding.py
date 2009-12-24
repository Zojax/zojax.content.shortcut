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
from zope.interface import Invalid
from zope.component import queryUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.security.interfaces import Unauthorized
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.container.browser.adding import Adding as BaseAdding

from zojax.content.browser.interfaces import _
from zojax.content.browser.utils import findContainer
from zojax.content.type.interfaces import IContentType
from zojax.content.type.constraints import checkContentType

from interfaces import IContentAdding


class Adding(BaseAdding):
    interface.implements(IContentAdding)

    title = _(u'Add content')

    layout_name = 'content-adding'

    def addingInfo(self):
        request = self.request
        container = self.context
        url = absoluteURL(container, request)

        contenttype = IContentType(container, None)

        if contenttype is None:
            return []

        result = []
        for ptype in contenttype.listContainedTypes():
            if ptype.addform:
                action = '%s/+/%s'%(url, ptype.addform)
            else:
                action = '%s/+/%s/'%(url, ptype.name)

            result.append({'id': ptype.name,
                           'title': ptype.title,
                           'description': ptype.description,
                           'selected': False,
                           'has_custom_add_view': True,
                           'action': action,
                           'icon': queryMultiAdapter(
                               (ptype, request), name='zmi_icon'),
                           'contenttype': ptype})

        result.sort(lambda a, b: cmp(a['title'], b['title']))
        return result

    def getContentType(self, name):
        ctype = queryUtility(IContentType, name)
        if ctype is not None:
            try:
                context = self.context
                ctype = ctype.__bind__(context)

                checkContentType(context, ctype)

                if ctype.isAvailable():
                    ctype.__name__ = name
                    ctype.__parent__ = self
                    return ctype
                else:
                    raise Unauthorized(ctype.permission)
            except Invalid:
                pass

    def publishTraverse(self, request, name):
        ctype = self.getContentType(name)
        if ctype is not None:
            return ctype

        return super(Adding, self).publishTraverse(request, name)

    def browserDefault(self, request):
        return self, ()
