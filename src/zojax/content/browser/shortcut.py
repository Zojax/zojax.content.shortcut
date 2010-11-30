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
from zope.security.tests.test_standard_checkers import check_forbidden_call
from zope.security.checker import canAccess
from zope.proxy import getProxiedObject, non_overridable
from zc.shortcut.interfaces import IObjectLinker
from zc.shortcut.factory import Factory
from zc.shortcut.shortcut import Shortcut
from zc.shortcut.proxy import TargetProxy, ProxyBase
from z3c.proxy.container import ContainerLocationProxy, proxify
from zojax.content.browser.tests.content import IContainer
from zojax.content.type.interfaces import IContentContainer
"""

$Id$
"""

    
def target(self):
    target = self.raw_target
    if IContentContainer.providedBy(target):
        return ContainerLocationProxy(target, self.__parent__, self.__name__)
    return TargetProxy(target, self.__parent__, self.__name__, self)

Shortcut.target = property(target)
