import icalendar
from datetime import datetime, timedelta
from zope.component import adapts
from zope.interface import implements

from plone.event.interfaces import (
    IEvent,
    IEventAccessor,
    IICalendarEventComponent
)
from plone.event.utils import pydt, utc


class ICalendarEventComponent(object):
    """ Returns an icalendar object of the event.

    """
    implements(IICalendarEventComponent)
    adapts(IEvent)

    def __init__(self, context):
        self.context = context
        self.event = IEventAccessor(context)

    def to_ical(self):

        ical = icalendar.Event()

        event = self.event

        # TODO: until VTIMETZONE component is added and TZID used, everything is
        #       converted to UTC. use real TZID, when VTIMEZONE is used!

        ical.add('dtstamp', utc(pydt(datetime.now())))
        ical.add('created', utc(pydt(event.creation_date)))

        # TODO: UID not present!
        ical.add('uid', event.uid)
        ical.add('last-modified', utc(pydt(event.modification_date)))
        ical.add('summary', event.title)

        if event.description: ical.add('description', event.description)

        if event.whole_day:
            ical.add('dtstart', utc(pydt(event.start)).date())
            ical.add('dtend', utc(pydt(event.end + timedelta(days=1))).date())
        else:
            ical.add('dtstart', utc(pydt(event.start)))
            ical.add('dtend', utc(pydt(event.end)))

        if event.recurrence:
            if event.recurrence.startswith('RRULE:'):
                recurrence = event.recurrence[6:]
            else:
                recurrence = event.recurrence
            ical.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

        if event.location: ical.add('location', event.location)

        # TODO: revisit and implement attendee export according to RFC
        if event.attendees:
            for attendee in event.attendees:
                ical.add('attendee', attendee)

        cn = []
        if event.contact_name:
            cn.append(event.contact_name)
        if event.contact_phone:
            cn.append(event.contact_phone)
        if event.contact_email:
            cn.append(event.contact_email)
        if event.event_url:
            cn.append(event.event_url)
        if cn:
            ical.add('contact', u', '.join(cn))

        if event.subjects:
            for subject in event.subjects:
                ical.add('categories', subject)

        return ical

