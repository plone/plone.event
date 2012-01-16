import mock
import unittest2 as unittest


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
        recrule = "FREQ=DAILY;INTERVAL=10;COUNT=5"
        seq = recurrence_sequence_ical(start, recrule=recrule)
        results = [res for res in seq]
        self.assertEqual(len(results), 5)

    def test_recrule_from_until(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = None
        from_ = datetime(2011, 11, 01)
        until = datetime(2011, 12, 31)
        seq = recurrence_sequence_ical(start, recrule=recrule, from_=from_, until=until)
        results = [res for res in seq]
        self.assertEqual(len(results), 1)

    def test_recrule_str_more_than_MAXCOUNT(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = "FREQ=DAILY;INTERVAL=10;COUNT=100001"
        seq = recurrence_sequence_ical(start, recrule=recrule)
        results = [res for res in seq]
        self.assertEqual(len(results), 100000)

    def test_recrule_str_more_than_count(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = "FREQ=DAILY;INTERVAL=10;COUNT=10"
        count = 5
        seq = recurrence_sequence_ical(start, recrule=recrule, count=count)
        results = [res for res in seq]
        self.assertEqual(len(results), 5)

    def test_recrule_from(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 23)
        recrule = "FREQ=DAILY;INTERVAL=1;COUNT=5"
        from_ = datetime(2011, 11, 25)
        until = datetime(2011, 11, 27)
        seq = recurrence_sequence_ical(start, recrule=recrule, from_=from_, until=until)
        results = [res for res in seq]
        self.assertEqual(len(results), 3)

    def test_recrule_until(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime
        start = datetime(2011, 11, 24)
        recrule = "FREQ=DAILY;INTERVAL=1;COUNT=5"
        from_ = datetime(2011, 11, 23)
        until = datetime(2011, 11, 27)
        seq = recurrence_sequence_ical(start, recrule=recrule, from_=from_, until=until)
        results = [res for res in seq]
        self.assertEqual(len(results), 4)

    def test_recrule_until_with_timezone(self):
        from plone.event.recurrence import recurrence_sequence_ical
        from datetime import datetime

        start = datetime(2011, 11, 24)
        recrule = "RRULE:FREQ=DAILY;UNTIL=20111130T000000Z"
        seq = list(recurrence_sequence_ical(start, recrule=recrule))
        self.assertEqual(len(seq), 7)
