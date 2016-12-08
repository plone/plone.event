# -*- coding: utf-8 -*-
from datetime import datetime
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from zope.configuration import xmlconfig

import pytz
import unittest
import zope.interface


class MockObject(object):
    """Mock object"""


class TestAdapters(unittest.TestCase):
    def setUp(self):
        import zope.component
        context = xmlconfig.file('meta.zcml', zope.component)
        xmlconfig.file('configure.zcml', zope.component, context=context)

        import plone.event
        xmlconfig.file('configure.zcml', plone.event, context=context)

    def test_event_accessor(self):
        obj = MockObject()
        tz = pytz.timezone('Europe/Vienna')
        obj.start = datetime(2012, 12, 12, 10, 0, tzinfo=tz)
        obj.end = datetime(2012, 12, 12, 12, 0, tzinfo=tz)
        zope.interface.alsoProvides(obj, IEvent)

        # Create accessor
        acc = IEventAccessor(obj)

        # Accessor getters
        self.assertEqual(acc.start, obj.start)
        self.assertEqual(acc.end, obj.end)
        self.assertEqual(acc.duration, obj.end - obj.start)

        # Accessor setters
        start = datetime(2013, 4, 5, 16, 31, tzinfo=tz)
        end = datetime(2013, 4, 5, 16, 35, tzinfo=tz)
        acc.start = start
        acc.end = end
        self.assertTrue(acc.start == obj.start == start)
        self.assertTrue(acc.end == obj.end == end)

        # Accessor deletor
        acc.something = True
        self.assertTrue(acc.something == obj.something is True)
        del acc.something
        self.assertTrue(hasattr(acc, 'something') is False)
        self.assertTrue(hasattr(obj, 'something') is False)

        del acc.start
        self.assertTrue(hasattr(acc, 'start') is False)
        self.assertTrue(hasattr(obj, 'start') is False)
