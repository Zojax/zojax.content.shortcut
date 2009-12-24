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
""" zojax.content.browser tests

$Id$
"""
import os, unittest, doctest
from zope.app.rotterdam import Rotterdam
from zope.app.testing.functional import ZCMLLayer
from zope.app.testing.functional import FunctionalDocFileSuite
from zojax.layoutform.interfaces import ILayoutFormLayer

zojaxContentBrowserLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'zojaxContentBrowserLayer', allow_teardown=True)


class IDefaultSkin(ILayoutFormLayer, Rotterdam):
    """ skin """


def test_suite():
    contents = FunctionalDocFileSuite(
        "contentsbrowser.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    contents.layer = zojaxContentBrowserLayer

    testbrowser = FunctionalDocFileSuite(
        "testbrowser.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    testbrowser.layer = zojaxContentBrowserLayer

    byline = FunctionalDocFileSuite(
        "byline.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    byline.layer = zojaxContentBrowserLayer

    return unittest.TestSuite((
        byline, contents, testbrowser,
        doctest.DocTestSuite(
            'zojax.content.browser.breadcrumb',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite(
            'zojax.content.browser.utils',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
