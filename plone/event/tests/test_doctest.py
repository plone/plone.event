# -*- coding: utf-8 -*-
from interlude import interact
from zope.component.testing import tearDown

import doctest
import os.path
import unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'recurrence.txt',
    # 'recurrence_support.txt',
    'recurrence_dateutil.txt',
    'utils.txt',
]
DOCMODS = [
    'plone.event.utils',
]

from DateTime import DateTime
from plone.event.utils import pydt


class FakeEvent(object):
    """ Fake Event for testing.
    """
    def __init__(self,
        attendees=[],
        contact_email=None,
        contact_name=None,
        contact_phone=None,
        created=None,
        description=None,
        end=None,
        end_date=None,
        event_url=None,
        location=None,
        modified=None,
        open_end=None,
        recurrence=None,
        start=None,
        start_date=None,
        subject=[],
        title=None,
        uid=None,
        whole_day=None,
    ):
        # start_date and end_date can be directly set with datetime values, if
        # no start or end DateTime is set.
        self.uid = uid
        self.title = title
        self.description = description
        self._start = start and DateTime(start) or None
        self.start_date = start and pydt(self._start) or start_date
        self._end = end and DateTime(end) or None
        self.end_date = end and pydt(self._end) or end_date
        self._whole_day = whole_day
        self._open_end = open_end
        self.created = created
        self.modified = modified
        self.location = location
        self.subject = subject
        self.attendees = attendees
        self.cname = contact_name
        self.cphone = contact_phone
        self.cemail = contact_email
        self.eurl = event_url
        self.recurrence = recurrence
        self.duration = self.start_date and self.end_date and\
                        self.end_date-self.start_date or None

    def start(self):
        return self._start

    def end(self):
        return self._end

    def whole_day(self):
        return self._whole_day

    def open_end(self):
        return self._open_end

    def Title(self):
        return self.title

    def Description(self):
        return self.description

    def CreationDate(self):
        return self.created

    def ModificationDate(self):
        return self.modified

    def getLocation(self):
        return self.location

    def Subject(self):
        return self.subject

    def getAttendees(self):
        return self.attendees

    def contact_name(self):
        return self.cname

    def contact_phone(self):
        return self.cphone

    def contact_email(self):
        return self.cemail

    def event_url(self):
        return self.eurl

    def UID(self):
        return self.uid


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            os.path.join(os.path.dirname(__file__), '..', docfile),
            module_relative=False,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact,
                   'FakeEvent': FakeEvent},
            tearDown=tearDown
        ) for docfile in DOCFILES
    ])
    suite.addTests([
        doctest.DocTestSuite(docmod,
                             optionflags=OPTIONFLAGS,
                             globs={'interact': interact,
                                    'FakeEvent': FakeEvent}
                             ) for docmod in DOCMODS
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
