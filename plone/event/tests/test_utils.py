import unittest

from plone.event import utils as event_util

from DateTime import DateTime

class FakeEvent(object):

    def __init__(self, start, end, whole_day):
        self._start = DateTime(start)
        self._end = DateTime(end)
        self._whole_day = whole_day

    def start(self):
        return self._start

    def end(self):
        return self._end

    def whole_day(self):
        return self._whole_day

class EventUtilsTests(unittest.TestCase):

    def _makeOne(self, start, end, whole_day=False):
        return FakeEvent(start, end, whole_day)

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
