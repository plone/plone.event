# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

import unittest
import doctest
from interlude import interact

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'recurrence.txt',
    'utils.txt',
]
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact,},
        ) for docfile in DOCFILES
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')