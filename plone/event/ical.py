from cStringIO import StringIO

from zope.component import getMultiAdapter
from zope.interface import implements
from Acquisition import aq_inner
from DateTime import DateTime

from plone.event.constants import (
    PRODID, ICS_HEADER, ICS_FOOTER, ICS_EVENT_START, ICS_EVENT_END)

from plone.event import utils

from plone.event.interfaces import IICalendar, IICalEventExporter


class DefaultICalendar(object):
    """Provides default hardcoded iCal header and footer"""
    
    implements(IICalendar)
    
    def __init__(self, context):
        self.context = context
    
    def header(self):
        return ICS_HEADER
    
    def footer(self):
        return ICS_FOOTER

class EventICalConverter(object):
    """Converts Event to and from iCal format"""
    
    implements(IICalEventExporter)

    def __init__(self, context):
        self.context = context

    def feed(self):
        # TODO: ensure non-ascii characters are working, internally we're woking
        # only with unicode srings, and return it in 'utf-8' at the end
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
