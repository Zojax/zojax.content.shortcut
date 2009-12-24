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
"""Setup for zojax.content.type package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name = 'zojax.content.browser',
      version = version,
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      description = "zojax content - Alternative implementation of content types system.",
      long_description = (
        'Detailed Documentation\n' +
        '======================\n'
        + '\n\n' +
        read('CHANGES.txt')
        ),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      url='http://zojax.net/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['zojax', 'zojax.content'],
      install_requires = ['setuptools',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'zope.app.publisher',
                          'z3c.breadcrumb',
                          'zojax.cache',
                          'zojax.content.type',
                          'zojax.content.forms',
                          'zojax.content.actions',
                          'zojax.principal.profile',
                          'zojax.formatter',
                          'zojax.layout',
                          'zojax.layoutform',
                          'zojax.statusmessage',
                          'zojax.pageelement',
                          'zojax.resource',
                          'zojax.resourcepackage',
                          'zojax.table',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.zcmlfiles',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  'zope.securitypolicy',
                                  'zojax.security',
                                  'zojax.autoinclude',
                                  'zojax.content.type [test]',
                                  'zojax.personal.content',
                                  'zojax.ui.breadcrumbs',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
