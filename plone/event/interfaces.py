# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#
__author__ = """Johannes Raggam <johannes@raggam.co.at>"""

from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.interface import Attribute
from zope import schema


class IEvent(Interface):
    """Generic calendar event for Plone.
    """
    start_date = Attribute(u"""Date when the first occurence of the event
                               begins as datetime object""")
    end_date = Attribute(u"""Date when the first occurence of the event ends as
                             datetime object""")


class IRecurringEvent(IEvent):
    """Generic recurring calendar event for Plone.
    """
    recurrence = Attribute(u'Recurrence definition')


class IRecurringEventICal(IRecurringEvent):
    """Marker interface for RFC2445 recurring events.
    """
    recurrence = Attribute(u"""Recurrence definition as RFC2445 compatible
                               string""")


class IRecurringEventTimeDelta(IRecurringEvent):
    """Marker interface for TimeDelta recurring events.
    """
    recurrence = Attribute(u"""Recurrence definition as delta from start in
                             minutes""")


class IRecurrenceSupport(Interface):
    """Interface for adapter providing recurrence support.
    """

    def occurences_start():
        """Returns all the event's start occurences which indicates the
           beginning of each event.
        """

    def occurences_end():
        """Returns all the event's end occurences which indicates the
           ending of each event.
        """

    def occurences():
        """Returns all the event's start and end occurences as a list of tuples.
        """

class IICalendar(Interface):
    """Provides header and footer for iCalendar format"""

    context = schema.Object(
        title=u"Any interface that might provide data for iCal header",
        description=u'',
        schema=IInterface
    )

    def header():
        """Returns iCal header"""
    
    def footer():
        """Returns iCal footer"""

class IICalEventExporter(Interface):
    """Serializes single event into iCalendar formatted entry.
    """
    
    context = schema.Object(
        title=u"Event",
        description=u'',
        schema=IEvent
    )
    
    def feed():
        """Returns ICal event entry, doesn't include iCal header, that should
        be done in application level level"""
