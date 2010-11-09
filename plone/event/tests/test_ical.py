import os
import unittest

from plone.event.ical import DefaultICalendar, EventICalExporter
from plone.event.constants import ICS_FOOTER, ICS_HEADER
from plone.event.utils import rfc2445dt

from DateTime import DateTime


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

class FakeEvent(object):

    def __init__(self, uid=None, title=None, description=None, start=None,
                 end=None, whole_day=None, created=None, modified=None,
                 location=None, subject=[], attendees=[], contact_name=None,
                 contact_phone=None, contact_email=None, event_url=None,
                 recurrence=None):
        self.uid = uid
        self.title = title
        self.description = description
        self._start = DateTime(start)
        self._end = DateTime(end)
        self._whole_day = whole_day
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

    def start(self):
        return self._start

    def end(self):
        return self._end

    def whole_day(self):
        return self._whole_day

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


class ICalExportTests(unittest.TestCase):

    def createEvent(self):
        return FakeEvent(uid='123456', title='Plone Conference',
            description='Annual Plone Conference',
            start='2010-10-25', end='2010-11-01',
            whole_day=True, created='2010-10-01',
            modified='2010-10-31',
            location='Bristol, UK', subject=['plone', 'cms'],
            attendees=['plonistas', 'devs'], contact_name='mat',
            contact_phone='11111111', contact_email='mat@netsight.net',
            event_url='http://www.ploneconf2010.org')

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def testDefaultICalendarHeader(self):
        event = FakeEvent(title='Test Event', description='desc')
        header = ICS_HEADER % dict(prodid=PRODID)
        header += u'X-WR-CALNAME:%s\n' % u'Test Event'
        header += u'X-WR-CALDESC:%s\n' % u'desc'
        self.assertEqual(DefaultICalendar(event).header(), header)

    def testDefaultICalendarHeader(self):
        self.assertEqual(DefaultICalendar(None).footer(), ICS_FOOTER)

    def testEventExporterFeed(self):
        data = EventICalExporter(self.createEvent()).feed()
        self.checkOrder(data,
            u'BEGIN:VEVENT',
            u'UID:ATEvent-123456',
            u'SUMMARY:Plone Conference',
            u'DTSTART:20101025',
            u'DTEND:20101102',
            u'DESCRIPTION:Annual Plone Conference',
            u'LOCATION:Bristol\, UK',
            u'CATEGORIES:plone,cms',
            u'ATTENDEE;CN="plonistas";ROLE=REQ-PARTICIPANT',
            u'ATTENDEE;CN="devs";ROLE=REQ-PARTICIPANT',
            u'CONTACT:mat\, 11111111\, mat@netsight.net',
            u'URL:http://www.ploneconf2010.org',
            u'CLASS:PUBLIC',
            u'END:VEVENT')

    def stestEventExporterGetICalSupplementaryMethod(self):
        event = self.createEvent()
        event.getICalSupplementary = lambda x: x.append(u'X-WR-CALBODY:text\n')
        data1 = EventICalExporter(event).feed()
        self.checkOrder(data,
            u'BEGIN:VEVENT',
            u'UID:ATEvent-123456',
            u'SUMMARY:Plone Conference',
            u'DTSTART:20101025',
            u'DTEND:20101102',
            u'DESCRIPTION:Annual Plone Conference',
            u'LOCATION:Bristol\, UK',
            u'CATEGORIES:plone,cms',
            u'ATTENDEE;CN="plonistas";ROLE=REQ-PARTICIPANT',
            u'ATTENDEE;CN="devs";ROLE=REQ-PARTICIPANT',
            u'CONTACT:mat\, 11111111\, mat@netsight.net',
            u'URL:http://www.ploneconf2010.org',
            u'X-WR-CALBODY:text',
            u'CLASS:PUBLIC',
            u'END:VEVENT')
        # self.assertEqual(data1.encode('utf-8'), data2 % {'dtstamp': dtstamp})

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ICalExportTests))
    return suite
