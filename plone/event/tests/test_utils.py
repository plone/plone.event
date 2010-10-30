import unittest

from plone.event import utils as event_util

from DateTime import DateTime

class FakeEvent(object):

    def __init__(self, start, end, wholeDay):
        self._start = DateTime(start)
        self._end = DateTime(end)
        self._wholeDay = wholeDay

    def start(self):
        return self._start

    def end(self):
        return self._end

    def getWholeDay(self):
        return self._wholeDay

class EventUtilsTests(unittest.TestCase):

    def _makeOne(self, start, end, wholeDay=False):
        return FakeEvent(start, end, wholeDay)

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

    def testToDisplayWithTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : '06:00 AM',
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : '06:00 PM',
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDaySameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00',
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : None,
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDayDifferentDays(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00',
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'end_date' : 'Oct 13, 2000',
                 'end_time' : None,
                 'same_day' : False,
                 'same_time' : False,
                })


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventUtilsTests))
    return suite
