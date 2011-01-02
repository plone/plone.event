import unittest

from plone.event import utils as event_util
from plone.event.tests.test_doctest import FakeEvent

class EventUtilsTests(unittest.TestCase):

    def _makeOne(self, start, end, whole_day=False):
        return FakeEvent(start=start, end=end, whole_day=whole_day)

    def testIsSameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameDay(event), True)

    def testIsSameDayFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00')
        self.assertEqual(event_util.isSameDay(event), False)

    def testIsSameTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 06:00:00')
        self.assertEqual(event_util.isSameTime(event), True)

    def testIsSameTimeFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameTime(event), False)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventUtilsTests))
    return suite
