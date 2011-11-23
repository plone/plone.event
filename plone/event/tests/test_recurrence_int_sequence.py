import mock
import unittest2 as unittest


class TestRecurrenceIntSequence(unittest.TestCase):

    @mock.patch('plone.event.recurrence.dt2int')
    def test_recrule_str_(self, dt2int):
        from plone.event.recurrence import recurrence_int_sequence
        sequence = [1, 2, 3]
        dt2int.return_value = 'a'
        res = [a for a in recurrence_int_sequence(sequence)]
        self.assertEqual(res, ['a', 'a', 'a'])
