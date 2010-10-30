from cStringIO import StringIO

from zope.component import getMultiAdapter
from zope.interface import implements
from Acquisition import aq_inner
from DateTime import DateTime

from plone.event.constants import (
    PRODID, ICS_HEADER, ICS_FOOTER, ICS_EVENT_START, ICS_EVENT_END)

from plone.event import utils

from plone.event.interfaces import IICalExporter, IICalEventExporter


class EventsICal(object):
    """Exports list of events into iCal format according to
    RFC2445 specification.
    """

    implements(IICalExporter)

    def __init__(self, events):
        self.events = events

    def __call__(self):
        data = ICS_HEADER % dict(prodid=PRODID)
        # TODO: ensure we have Title and Description declared by IEvent
        #data += 'X-WR-CALNAME:%s\n' % context.Title()
        #data += 'X-WR-CALDESC:%s\n' % context.Description()
        for event in self.events:
            data += IICalEventExporter(event)()
        data += ICS_FOOTER
        return data

class EventICal(object):
    """See interface"""
    
    implements(IICalEventExporter)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        start_str, end_str = utils.dateStringsForEvent(self.context)
        out = StringIO()
        map = {
            'dtstamp'   : utils.rfc2445dt(DateTime()),
            'created'   : utils.rfc2445dt(DateTime(self.context.CreationDate())),
            'uid'       : self.context.UID(),
            'modified'  : utils.rfc2445dt(DateTime(self.context.ModificationDate())),
            'summary'   : utils.vformat(self.context.Title()),
            'startdate' : start_str,
            'enddate'   : end_str,
            }
        out.write(ICS_EVENT_START % map)

        description = self.context.Description()
        if description:
            out.write(utils.foldline('DESCRIPTION:%s\n' % utils.vformat(description)))

        location = self.context.getLocation()
        if location:
            out.write('LOCATION:%s\n' % utils.vformat(location))

        subject = self.context.Subject()
        if subject:
            out.write('CATEGORIES:%s\n' % ','.join(subject))

        attendees = self.context.getAttendees()
        for attendee in attendees:
            out.write('ATTENDEE;CN="%s";ROLE=REQ-PARTICIPANT\n'%utils.vformat(attendee))


        # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)

        cn = []
        contact = self.context.contact_name()
        if contact:
            cn.append(contact)
        phone = self.context.contact_phone()
        if phone:
            cn.append(phone)
        email = self.context.contact_email()
        if email:
            cn.append(email)
        if cn:
            out.write('CONTACT:%s\n' % utils.vformat(', '.join(cn)))

        url = self.context.event_url()
        if url:
            out.write('URL:%s\n' % url)

        # allow derived event types to inject additional data for iCal
        try:
            self.context.getICalSupplementary(out)
        except AttributeError:
            pass

        out.write(ICS_EVENT_END)
        return out.getvalue()
