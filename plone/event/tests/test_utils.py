import mock
import unittest2 as unittest


class TestUtils(unittest.TestCase):

    @mock.patch('plone.event.utils.pytz')
    @mock.patch('plone.event.utils.os')
    def test_default_timezone(self, os, pytz):
        from plone.event.utils import default_timezone
        os.environ.keys.return_value = ['TZ']
        os.environ = mock.MagicMock()
        pytz.timezone().zone = 'zone'
        self.assertEqual(default_timezone(), 'zone')

    @mock.patch('plone.event.utils.isSameDay')
    @mock.patch('plone.event.utils.rfc2445dt')
    def test_dateStringsForEvent__whole_day_isSameDay(self, rfc2445dt, isSameDay):
        from plone.event.utils import dateStringsForEvent
        event = mock.MagicMock()
        rfc2445dt.return_value = 'str'
        self.assertEqual(
            dateStringsForEvent(event),
            ('str', 'str')
        )

    @mock.patch('plone.event.utils.isSameDay')
    @mock.patch('plone.event.utils.rfc2445dt')
    def test_dateStringsForEvent__whole_day_not_SameDay(self, rfc2445dt, isSameDay):
        from plone.event.utils import dateStringsForEvent
        event = mock.MagicMock()
        rfc2445dt.return_value = 'str'
        isSameDay.return_value = False
        self.assertEqual(
            dateStringsForEvent(event),
            ('str', 'str')
        )

    @mock.patch('plone.event.utils.isSameDay')
    @mock.patch('plone.event.utils.rfc2445dt')
    def test_dateStringsForEvent__not_whole_day(self, rfc2445dt, isSameDay):
        from plone.event.utils import dateStringsForEvent
        event = mock.MagicMock()
        event.whole_day.return_value = False
        rfc2445dt.return_value = 'str'
        self.assertEqual(
            dateStringsForEvent(event),
            ('str', 'str')
        )

    def test_utcoffset_normalize(self):
        from plone.event.utils import utcoffset_normalize
        date = mock.Mock()
        date.replace = mock.Mock(side_effect=KeyError)
        self.assertEqual(
            utcoffset_normalize(date),
            date
        )

    def test_dt2DT(self):
        from plone.event.utils import dt2DT
        from datetime import datetime
        dt = datetime(2011, 11, 23)
        from DateTime import DateTime
        DT = DateTime(2011, 11, 23)
        self.assertEqual(
            dt2DT(dt),
            DT
        )

    @mock.patch('plone.event.utils.guesstz')
    @mock.patch('plone.event.utils.utctz')
    def test_pydt__missing_zone_is_None(self, utctz, guesstz):
        from plone.event.utils import pydt
        dt = mock.Mock()
        dt.toZone.return_value = dt
        dt.parts.return_value = (2011, 11, 24, 11, 39, 00)
        guesstz.return_value = None
        import pytz
        utctz.return_value = pytz.timezone('UTC')
        pydt(dt)
        self.assertTrue(utctz.called)

    @mock.patch('plone.event.utils.guesstz')
    @mock.patch('plone.event.utils.utctz')
    def test_pydt__missing_zone_is_not_None(self, utctz, guesstz):
        from plone.event.utils import pydt
        dt = mock.Mock()
        import pytz
        utctz.return_value = pytz.timezone('UTC')
        missing_zone = utctz()
        dt.toZone.return_value = dt
        dt.parts.return_value = (2011, 11, 24, 11, 39, 00)
        guesstz.return_value = None
        pydt(dt, missing_zone=missing_zone)
        self.assertEqual(utctz.call_count, 1)

    def test_dt2int_dt_is_None(self):
        from plone.event.utils import dt2int
        self.assertFalse(dt2int(None))

    @mock.patch('plone.event.utils.MAX32', 0)
    @mock.patch('plone.event.utils.utc')
    def test_dt2int_less_MAX32(self, utc):
        from plone.event.utils import dt2int
        dt = mock.Mock()
        dd = mock.Mock()
        utc.return_value = dd
        dd.year = 2011
        dd.month = 11
        dd.day = 24
        dd.hour = 14
        dd.minute = 16
        self.assertRaises(OverflowError, lambda: dt2int(dt))

    @mock.patch('plone.event.utils.MAX32', 1077778937)
    @mock.patch('plone.event.utils.utc')
    def test_dt2int_more_MAX32(self, utc):
        from plone.event.utils import dt2int
        dt = mock.Mock()
        dd = mock.Mock()
        utc.return_value = dd
        dd.year = 2011
        dd.month = 11
        dd.day = 24
        dd.hour = 14
        dd.minute = 16
        value = 1077778936
        self.assertEqual(dt2int(dt), value)
