from Acquisition import aq_inner
# TODO: probably get rid of DateTime dependency here
from DateTime import DateTime

from zope.interface import implements

# TODO: remove any dependency on CMFPlone
from Products.CMFPlone.utils import safe_unicode

from plone.event.constants import PRODID, ICS_HEADER, ICS_FOOTER, \
    ICS_EVENT_START, ICS_EVENT_END
from plone.event.utils import dateStringsForEvent, vformat, rfc2445dt, foldline
from plone.event.interfaces import IICalendar, IICalEventExporter


class DefaultICalendar(object):
    """Provides default hardcoded iCal header and footer"""

    implements(IICalendar)

    def __init__(self, context):
        self.context = context

    def header(self):
        data = ICS_HEADER % dict(prodid=PRODID)
        data += u'X-WR-CALNAME:%s\n' % safe_unicode(self.context.Title())
        data += u'X-WR-CALDESC:%s\n' % safe_unicode(self.context.Description())
        return data

    def footer(self):
        return ICS_FOOTER

class EventICalExporter(object):
    """Converts Event to and from iCal format"""

    implements(IICalEventExporter)

    def __init__(self, context):
        self.context = context

    def feed(self):
        context = aq_inner(self.context)
        start_str, end_str = dateStringsForEvent(context)
        out = []
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(context.CreationDate())),
            'uid'       : context.UID(),
            'modified'  : rfc2445dt(DateTime(context.ModificationDate())),
            'summary'   : vformat(safe_unicode(context.Title())),
            'startdate' : start_str,
            'enddate'   : end_str,
            'recurrence': context.recurrence,
            }
        out.append(ICS_EVENT_START % map)

        description = context.Description()
        if description:
            out.append(foldline(u'DESCRIPTION:%s\n' %
                vformat(safe_unicode(description))))

        location = context.getLocation()
        if location:
            out.append(u'LOCATION:%s\n' % vformat(safe_unicode(location)))

        subject = context.Subject()
        if subject:
            out.append(u'CATEGORIES:%s\n' % u','.join(subject))

        # TODO: revisit and implement attendee export according to RFC
        attendees = context.getAttendees()
        for attendee in attendees:
            out.append(u'ATTENDEE;CN="%s";ROLE=REQ-PARTICIPANT\n' %
                vformat(safe_unicode(attendee)))

        cn = []
        contact = context.contact_name()
        if contact:
            cn.append(safe_unicode(contact))
        phone = context.contact_phone()
        if phone:
            cn.append(phone)
        email = context.contact_email()
        if email:
            cn.append(email)
        if cn:
            out.append(u'CONTACT:%s\n' % vformat(u', '.join(cn)))

        url = context.event_url()
        if url:
            out.append(u'URL:%s\n' % url)

        # allow derived event types to inject additional data for iCal
        if hasattr(self.context, 'getICalSupplementary'):
            context.getICalSupplementary(out)

        out.append(ICS_EVENT_END)
        return u''.join(out)
