# -*- coding: utf-8 -*-
from zope.component.testing import tearDown

import doctest
import os.path
import unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'recurrence.txt',
    'recurrence_dateutil.txt',
    'utils.txt',
]
DOCMODS = ['plone.event.utils', ]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            doctest.DocFileSuite(
                os.path.join(os.path.dirname(__file__), '..', docfile),
                module_relative=False,
                optionflags=OPTIONFLAGS,
                tearDown=tearDown
            )
            for docfile in DOCFILES
        ]
    )
    suite.addTests(
        [
            doctest.DocTestSuite(
                docmod, optionflags=OPTIONFLAGS
            )
            for docmod in DOCMODS
        ]
    )
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
