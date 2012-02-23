from zope.interface import Interface, Attribute

class IVEvent(Interface):
    """ RFC5545 Event schema

    ; The following are REQUIRED,
    ; but MUST NOT occur more than once.
    ;
    dtstamp / uid /
    ;
    ; The following is REQUIRED if the component
    ; appears in an iCalendar object that doesn't
    ; specify the "METHOD" property; otherwise, it
    ; is OPTIONAL; in any case, it MUST NOT occur
    ; more than once.
    ;
    dtstart /
    ;
    ; The following are OPTIONAL,
    ; but MUST NOT occur more than once.
    ;
    class / created / description / geo /
    last-mod / location / organizer / priority /
    seq / status / summary / transp /
    url / recurid /
    ;
    ; The following is OPTIONAL,
    ; but SHOULD NOT occur more than once.
    ;
    rrule /
    ;
    ; Either 'dtend' or 'duration' MAY appear in
    ; a 'eventprop', but 'dtend' and 'duration'
    ; MUST NOT occur in the same 'eventprop'.
    ;
    dtend / duration /
    ;
    ; The following are OPTIONAL,
    ; and MAY occur more than once.
    ;
    attach / attendee / categories / comment /
    contact / exdate / rstatus / related /
    resources / rdate / x-prop / iana-prop

    """
    dtstart = Attribute(u"Start Date/Time")
    dtend = Attribute(u"End Date/Time")
    duration = Attribute(u"Duration")
    rrule = Attribute(u"Recurrence Rule")
    description = Attribute(u"Description")
    location = Attribute(u"Location")
    summary = Attribute(u"Summary")
    url = Attribute(u"Url")
    attendee = Attribute(u"Attendee")
    categories = Attribute(u"Categories")
    contact = Attribute(u"Contact")

    exdate = Attribute(u"Exdate")
    rdate = Attribute(u"Rdate")

    dtstamp = Attribute(u"Timestamp")
    uid = Attribute(u"Unique identifier")
    klass = Attribute(u"Class") # class
    created = Attribute(u"Created")
    geo = Attribute(u"Geo")
    last_mod = Attribute(u"Last Modified") # last-mod
    organizer = Attribute(u"Organizer")
    priority = Attribute(u"Priority")
    seq = Attribute(u"Seq")
    status = Attribute(u"Status")
    transp = Attribute(u"Transp")
    recurid = Attribute(u"Recurid")
    attach = Attribute(u"Attach")
    comment = Attribute(u"Comment")
    rstatus = Attribute(u"Rstatus")
    related = Attribute(u"Related")
    resources = Attribute(u"Resources")
    x_prop = Attribute(u"X Prop") # x-prop
    iana_prop = Attribute(u"Iana Prop") # iana-prop


    start = Attribute(u"Event start date")
    end = Attribute(u"Event end date")
    timezone = Attribute(u"Timezone of the event")
    recurrence = Attribute(u"RFC5545 compatible recurrence definition")
    whole_day = Attribute(u"Event lasts whole day")
    location = Attribute(u"Location of the event")
    text = Attribute(u"Summary of the event")
    attendees = Attribute(u"List of attendees")
    event_url = Attribute(u"Website of the event")
    contact_name = Attribute(u"Contact name")
    contact_email = Attribute(u"Contact email")
    contact_phone = Attribute(u"Contact phone")
