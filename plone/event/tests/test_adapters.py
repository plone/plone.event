import unittest2 as unittest
from zope.configuration import xmlconfig
from plone.event.interfaces import IEvent, IEventAccessor
from datetime import datetime
import pytz
import zope.interface


class MockObject(object):
    """ Mock object

    """

class TestAdapters(unittest.TestCase):

    def setUp():
        import plone.event
        xmlconfig("configure.zcml", plone.event)

    def test_event_accessor(self):
        obj = MockObject()
        tz = pytz.timezone("Europe/Vienna")
        obj.start = datetime(2012,12,12,10,0,tzinfo=tz)
        obj.end = datetime(2012,12,12,12,0,tzinfo=tz)
        zope.interface.alsoProvides(obj, IEvent)
        acc = IEventAccessor(obj)
        self.assertTrue(acc.start == obj.start)
        self.assertTrue(acc.end == obj.end)
        self.assertTrue(acc.duration == obj.end - obj.start)
