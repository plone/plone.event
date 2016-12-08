# -*- coding: utf-8 -*-
import unittest


class TestRecurrenceSequenceIcal(unittest.TestCase):
    def test_start(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        seq = recurrence_sequence_ical(start)
        results = [res for res in seq]
        self.assertEqual(len(results), 1)

    def test_recrule_str(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = 'FREQ=DAILY;INTERVAL=10;COUNT=5'
        seq = recurrence_sequence_ical(start, recrule=recrule)
        results = [res for res in seq]
        self.assertEqual(len(results), 5)

    def test_recrule_str_rdate(self):
        """Test, if an RDATE date has the correct time set.
            See: "BUGFIX WRONG RDATE TIME" in recurrence.py
        """
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23, 10, 10)
        recrule = """FREQ=DAILY;INTERVAL=1;COUNT=3
RDATE:20111129T000000"""
        seq = recurrence_sequence_ical(start, recrule=recrule)
        results = [res for res in seq]
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].time(), results[-1].time())

    def test_recrule_str_exdate(self):
        """Test, if an EXDATE date are not in the resulting recurrence set.
        """
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        import pytz
        at = pytz.timezone('Europe/Vienna')
        start = at.localize(datetime(2013, 6, 29, 10, 10))
        recrule = 'RRULE:FREQ=DAILY;COUNT=4\r\nEXDATE:20130630T000000,20130701T000000\r\nRDATE:20130706T000000,20130809T000000'  # noqa
        seq = recurrence_sequence_ical(start, recrule=recrule)
        res = [res for res in seq]
        res_test = [
            at.localize(datetime(2013, 6, 29, 10, 10)),
            at.localize(datetime(2013, 7, 2, 10, 10)),
            at.localize(datetime(2013, 7, 6, 10, 10)),
            at.localize(datetime(2013, 8, 9, 10, 10))
        ]
        self.assertEqual(len(res), 4)
        self.assertEqual(res, res_test)

    def test_recrule_str_until(self):
        """Test, if UNTIL stops the sequence at the end of the day, even if
        it's set to 0:00 by the recurrence widget.
        """
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        import pytz
        at = pytz.timezone('Europe/Vienna')
        start = at.localize(datetime(2013, 6, 29, 10, 10))
        recrule = 'RRULE:FREQ=DAILY;UNTIL=20130702T000000'
        seq = recurrence_sequence_ical(start, recrule=recrule)
        res = [res for res in seq]
        res_test = [
            at.localize(datetime(2013, 6, 29, 10, 10)),
            at.localize(datetime(2013, 6, 30, 10, 10)),
            at.localize(datetime(2013, 7, 1, 10, 10)),
            at.localize(datetime(2013, 7, 2, 10, 10))
        ]
        self.assertEqual(len(res), 4)
        self.assertEqual(res, res_test)

    def test_recrule_from_until(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = None
        from_ = datetime(2011, 11, 1)
        until = datetime(2011, 12, 31)
        seq = recurrence_sequence_ical(
            start,
            recrule=recrule,
            from_=from_,
            until=until,
        )
        results = [res for res in seq]
        self.assertEqual(len(results), 1)

    def test_recrule_str_more_than_MAXCOUNT(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = 'FREQ=DAILY;INTERVAL=10;COUNT=1001'
        seq = recurrence_sequence_ical(start, recrule=recrule)
        results = [res for res in seq]
        self.assertEqual(len(results), 1000)

    def test_recrule_str_more_than_count(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = 'FREQ=DAILY;INTERVAL=10;COUNT=10'
        count = 5
        seq = recurrence_sequence_ical(start, recrule=recrule, count=count)
        results = [res for res in seq]
        self.assertEqual(len(results), 5)

    def test_recrule_from(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = 'FREQ=DAILY;INTERVAL=1;COUNT=5'
        from_ = datetime(2011, 11, 25)
        until = datetime(2011, 11, 27)
        seq = recurrence_sequence_ical(
            start,
            recrule=recrule,
            from_=from_,
            until=until,
        )
        results = [res for res in seq]
        self.assertEqual(len(results), 3)

    def test_recrule_until(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 24)
        recrule = 'FREQ=DAILY;INTERVAL=1;COUNT=5'
        from_ = datetime(2011, 11, 23)
        until = datetime(2011, 11, 27)
        seq = recurrence_sequence_ical(
            start,
            recrule=recrule,
            from_=from_,
            until=until,
        )
        results = [res for res in seq]
        self.assertEqual(len(results), 4)

    def test_recrule_from_until_with_duration(self):
        """Should include events ranging into the queried timerange.
        """
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        from datetime import timedelta
        start = datetime(2011, 11, 23)
        recrule = 'FREQ=DAILY;INTERVAL=1;COUNT=5'
        from_ = datetime(2011, 11, 26)
        until = datetime(2011, 11, 27)
        seq = recurrence_sequence_ical(
            start,
            recrule=recrule,
            from_=from_,
            until=until,
            duration=timedelta(days=2),
        )
        results = [res for res in seq]
        self.assertEqual(len(results), 4)

    def test_recrule_until_with_timezone(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime

        start = datetime(2011, 11, 24)
        recrule = 'RRULE:FREQ=DAILY;UNTIL=20111130T000000Z'
        seq = list(recurrence_sequence_ical(start, recrule=recrule))
        self.assertEqual(len(seq), 7)
