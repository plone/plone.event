# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

import unittest
import doctest
from zope.component.testing import tearDown
from interlude import interact

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'recurrence.txt',
    'recurrence_support.txt',
    'utils.txt',
]

from zope.interface import implements
from plone.event.interfaces import IRecurringEventICal
class MockEvent(object):
    """Basic stub object for testing events.
    """
    implements(IRecurringEventICal)
    def __init__(self, recurrence=None, start_date=None, end_date=None):
        self.recurrence = recurrence
        self.start_date = start_date
        self.end_date = end_date
        self.duration = end_date - start_date
        #subject
        #location
        #wholeDay
        #startDate
        #endDate
        #text
        #attendees
        #eventUrl
        #contactName
        #contactEmail
        #contactPhone
        #recurrence
        #start_date
        #end_date
        #duration

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact,},
            tearDown=tearDown
        ) for docfile in DOCFILES
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
