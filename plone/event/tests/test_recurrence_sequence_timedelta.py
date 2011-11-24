import unittest2 as unittest


class TestRecurrenceSequenceTimedelta(unittest.TestCase):

    def test_delta_None(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        until = datetime(2011, 11, 24)
        td = recurrence_sequence_timedelta(start, until=until)
        results = [res for res in td]
        self.assertEqual(len(results), 1)

    def test_delta_zero(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        delta = 0
        until = datetime(2011, 11, 24)
        td = recurrence_sequence_timedelta(start, delta=delta, until=until)
        results = [res for res in td]
        self.assertEqual(len(results), 1)

    def test_until_None(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        delta = 1
        td = recurrence_sequence_timedelta(start, delta=delta)
        results = [res for res in td]
        self.assertEqual(len(results), 1)

    def test_delta_an_hour_until_next_day(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        delta = 60
        until = datetime(2011, 11, 24)
        td = recurrence_sequence_timedelta(start, delta=delta, until=until)
        results = [res for res in td]
        self.assertEqual(len(results), 25)

    def test_recur_more_than_MAXCOUNT(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        delta = 1
        until = datetime(2012, 11, 23)
        td = recurrence_sequence_timedelta(start, delta=delta, until=until)
        results = [res for res in td]
        self.assertEqual(len(results), 100001)

    def test_recur_more_than_count(self):
        from plone.event.recurrence import recurrence_sequence_timedelta
        from datetime import datetime
        start = datetime(2011, 11, 23)
        delta = 1
        until = datetime(2011, 11, 24)
        count = 20
        td = recurrence_sequence_timedelta(start, delta=delta, until=until, count=count)
        results = [res for res in td]
        self.assertEqual(len(results), 21)
