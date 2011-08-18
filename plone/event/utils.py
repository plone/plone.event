# -*- coding: utf-8 -*-

import textwrap


def foldline(text, lenght=70):
    """ Make a string folded per RFC5545 (each line must be less than 75 octets)

    >>> from plone.event.utils import foldline
    >>> foldline('foo')
    u'foo\\n'

    >>> longtext = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    ...             "Vestibulum convallis imperdiet dui posuere.")
    >>> foldline(longtext)
    u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum co\\n
    nvallis imperdiet dui posuere.\\n'

    """
    return '\n'.join(
            textwrap.wrap(text, lenght,
                subsequent_indent='  ',
                drop_whitespace=True,
                )
            )

import os
import time
import pytz
import warnings


def default_timezone():
    """ Retrieve the timezone from the server.
        Default Fallback: UTC

        >>> from zope.component import getUtility
        >>> from plone.event.interfaces import ITimezoneGetter
        >>> tzgetter = getUtility(ITimezoneGetter, 'FallbackTimezoneGetter')
        >>> import os
        >>> import time
        >>> timetz = time.tzname
        >>> ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None

        >>> os.environ['TZ'] = "Europe/Vienna"
        >>> tzgetter().timezone
        'Europe/Vienna'

        >>> os.environ['TZ'] = ""
        >>> time.tzname = None
        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...    warnings.simplefilter("always")
        ...    tzgetter().timezone
        ...    assert(len(w) == 1)
        ...    assert(issubclass(w[-1].category, RuntimeWarning))
        ...    assert("timezone" in str(w[-1].message))
        'UTC'

        >>> time.tzname = ('CET', 'CEST')
        >>> tzgetter().timezone
        'CET'

        >>> time.tzname = timetz
        >>> if ostz:
        ...     os.environ['TZ'] = ostz
        ... else:
        ...     del os.environ['TZ']

    """

    timezone = None
    if 'TZ' in os.environ.keys():
        # Timezone from OS env var
        timezone = os.environ['TZ']
    if not timezone:
        # Timezone from python time
        zones = time.tzname
        if zones and len(zones) > 0:
            timezone = zones[0]
        else:
            # Default fallback = UTC
            warnings.warn("Operating system's timezone cannot be found"\
                          "- using UTC.", RuntimeWarning)
            timezone = 'UTC'
    # following statement ensures, that timezone is a valid pytz zone
    return pytz.timezone(timezone).zone




# for plone.app.event

    @property
    def is_same_time(self):
        return self.context.start.time() == self.context.end.time()

    @property
    def is_same_day(self):
        return self.context.start.year == self.context.end.year and \
               self.context.start.month == self.context.end.month and \
               self.context.start.day == self.context.end.day

    # ical/vcal string

    @property
    def body(self):
        out = []

        if self.context.whole_day:
            # For all-day events we must not include the time within
            # the date-time string
            start = convert_to_rfc2445_string(self.context.start,
                        mode="float", time=False)
            if self.is_same_day:
                # one-day events end with the timestamp of the next day
                # (which is the start data plus 1 day)
                end = convert_to_rfc2445_string(self.context.start + 1,
                            mode="float", time=False)
            else:
                # all-day events lasting several days end at the next
                # day after the end date
                end = convert_to_rfc2445_string(self.context.end + 1,
                            mode="float", time=False)
        else:
            # default
            start = convert_to_rfc2445_string(self.context.start)
            end = convert_to_rfc2445_string(self.context.end)

        out.append(self.EVENT_START % {
            'dtstamp'   : convert_to_rfc2445_string(datetime.today()),
            'created'   : convert_to_rfc2445_string(self.context.creation_date),
            'modified'  : convert_to_rfc2445_string(self.context.modification_date),
            'uid'       : self.context.uid,
            'summary'   : self.escape(self.context.summary),
            'startdate' : start,
            'enddate'   : end,
            })

        if self.context.recurrence:
            out.append(self.context.recurrence)

        if self.context.description:
            out.append(self.foldline(u'DESCRIPTION:' + self.context.description))

        if self.context.location:
            out.append(u'LOCATION:%s' % self.escape(self.context.location))

        if self.context.categories:
            out.append(u'CATEGORIES:%s' % u','.join(self.context.categories))

        # XXX: maybe we should extends to support more iCal options here
        for attendee in self.context.attendees:
            out.append(u'ATTENDEE;CN="%s";ROLE=REQ-PARTICIPANT' %
                    self.escape(attendee))

        contact = []
        if self.context.contact_name:
            contact.append(self.context.contact_name)
        if self.context.contact_phone:
            contact.append(self.context.contact_phone)
        if self.context.contact_email:
            contact.append(self.context.contact_email)
        if contact:
            out.append(self.foldline(u'CONTACT:%s' % self.escape(u', '.join(cn))))

        if self.context.url:
            out.append(u'URL:%s' % self.context.url)

        out.append(self.EVENT_END)

        # allow derived event types to inject additional data for iCal
        if hasattr(self.context, 'event_ical_customize'):
            out = getattr(self.context, 'event_ical_customize')(out)

        return u'\n'.join(out)


import pytz
from datetime import datetime
from datetime import timedelta

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'
MAX32 = int(2**31 - 1)

# >>> interact(locals(), use_ipython=False )

### Display helpers
def isSameTime(event):
    """ Test if event starts and ends at same time.

    >>> from plone.event.tests.test_doctest import FakeEvent
    >>> from plone.event.utils import isSameTime
    >>> isSameTime(FakeEvent(start='2000/01/01 06:00:00',
    ...                      end='2010/02/02 06:00:00'))
    True
    >>> from plone.event.tests.test_doctest import FakeEvent
    >>> from plone.event.utils import isSameTime
    >>> isSameTime(FakeEvent(start='2000/10/12 06:00:00',
    ...                      end='2000/10/12 18:00:00'))
    False

    """
    return event.start().time == event.end().time

def isSameDay(event):
    """ Test if event starts and ends at same day.

    >>> from plone.event.tests.test_doctest import FakeEvent
    >>> from plone.event.utils import isSameDay
    >>> isSameDay(FakeEvent(start='2000/10/12 06:00:00',
    ...                     end='2000/10/12 18:00:00'))
    True
    >>> isSameDay(FakeEvent(start='2000/10/12 06:00:00',
    ...                     end='2000/10/13 18:00:00'))
    False

    """
    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()

def dateStringsForEvent(event):
    # Smarter handling for whole-day events
    if event.whole_day():
        # For all-day events we must not include the time within
        # the date-time string
        start_str = rfc2445dt(event.start(), mode="float", time=False)
        if isSameDay(event):
            # one-day events end with the timestamp of the next day
            # (which is the start data plus 1 day)
            end_str = rfc2445dt(event.start() + 1, mode="float", time=False)
        else:
            # all-day events lasting several days end at the next
            # day after the end date
            end_str = rfc2445dt(event.end() + 1, mode="float", time=False)
    else:
        # default (as used in Plone)
        start_str = rfc2445dt(event.start())
        end_str = rfc2445dt(event.end())

    return start_str, end_str


### RFC2445 export helpers
def rfc2445dt(dt, mode='utc', date=True, time=True):
    """ Convert a datetime or DateTime object into an RFC2445 compatible
    datetime string.

    @param dt: datetime or DateTime object to convert.

    @param mode: Conversion mode ('utc'|'local'|'float')
        Mode 'utc':   Return datetime string in UTC
        Mode 'local': Return datetime string as local including a TZID component
        Mode 'float': Return datetime string as floating (local without TZID
                      component)

    @param date: Return date.

    @param time: Return time.

    Usage
    =====

    >>> from datetime import datetime
    >>> import pytz # this import actually takes quite a long time!
    >>> from plone.event.utils import rfc2445dt

    >>> at = pytz.timezone('Europe/Vienna')
    >>> dt = at.localize(datetime(2010,10,10,10,10))
    >>> dt
    datetime.datetime(2010, 10, 10, 10, 10, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

    >>> assert(rfc2445dt(dt) == rfc2445dt(dt, mode='utc'))
    >>> rfc2445dt(dt)
    '20101010T081000Z'

    >>> rfc2445dt(dt, mode='local')
    ('20101010T101000', 'Europe/Vienna')

    >>> rfc2445dt(dt, mode='float')
    '20101010T101000'

    >>> assert(rfc2445dt(dt, date=True, time=True) == rfc2445dt(dt))
    >>> rfc2445dt(dt, time=False)
    '20101010Z'
    >>> rfc2445dt(dt, date=False)
    '081000Z'

    RFC2445 dates from DateTime objects
    -----------------------------------
    >>> from DateTime import DateTime

    It's summer time! So TZ in Belgrade is GMT+2.
    >>> rfc2445dt(DateTime('2010/08/31 18:00:00 Europe/Belgrade'))
    '20100831T160000Z'

    GMT offsets are converted to UTC without any DST adjustments.
    >>> rfc2445dt(DateTime('2010/08/31 20:15:00 GMT+1'))
    '20100831T191500Z'

    """
    dt = pydt(dt)
    if mode == 'utc': dt = utc(dt)
    date = "%s%s%s%s" % (date and dt.strftime("%Y%m%d") or '',
                         date and time and 'T' or '',
                         time and dt.strftime("%H%M%S") or '',
                         mode=='utc' and 'Z' or '')
    if mode == 'local': return date, dt.tzinfo.zone
    return date


def vformat(s):
    """ Escape special chars for use in vcal/ical files.

    >>> from plone.event.utils import vformat
    >>> vformat('foo')
    u'foo'
    >>> vformat('foo,bar')
    u'foo\\\\,bar'
    >>> vformat('foo;bar')
    u'foo\\\\;bar'
    >>> vformat('foo:bar')
    u'foo\\\\:bar'
    >>> vformat('foo:bar,more')
    u'foo\\\\:bar\\\\,more'
    """
    return s.strip().replace(u',', u'\,').replace(u':', u'\:'
        ).replace(u';', u'\;')


### Timezone helpers
def utctz():
    return pytz.timezone('UTC')

def utc(dt):
    """Convert Python datetime to UTC."""
    if dt is None:
        return None
    return dt.astimezone(utctz())

def utcoffset_normalize(date, delta=None, dstmode=DSTAUTO):
    """Fixes invalid UTC offsets from recurrence calculations.

    @param date: datetime instance to normalize.

    @param delta: datetime.timedelta instance.
    Mode DSTADJUST: When crossing daylight saving time changes, the start time
        of the date before DST change will be the same in value as afterwards.
        It is adjusted relative to UTC. So 8:00 GMT+1 before will also result in
        8:00 GMT+2 afterwards. This is what humans might expect when recurring
        rules are defined.
    Mode DSTKEEP: When crossing daylight saving time changes, the start time of
        the date before and after DST change will be the same relative to UTC.
        So, 8:00 GMT+1 before will result in 7:00 GMT+2 afterwards. This
        behavior might be what machines expect, when recurrence rules are
        defined.
    Mode DSTAUTO:
        If the relative delta between two occurences of a reucurrence sequence
        is less than a day, DSTKEEP will be used - otherwise DSTADJUST. This
        behavior is the default.

    """
    try:
        assert(bool(date.tzinfo))
    except:
        raise TypeError('Cannot normalize timezone naive dates')
    assert(dstmode in [DSTADJUST, DSTKEEP, DSTAUTO])
    if delta:
        assert(isinstance(delta, timedelta)) # Easier in Java
        delta = delta.seconds + delta.days*24*3600 # total delta in seconds
        if dstmode==DSTAUTO and delta<24*60*60:
            dstmode = DSTKEEP
        elif dstmode==DSTAUTO:
            dstmode = DSTADJUST

    try:
        if dstmode==DSTKEEP:
            return date.tzinfo.normalize(date)
        else: # DSTADJUST
            return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    except:
        # TODO: python-datetime converts e.g RDATE:20100119T230000Z to
        # datetime.datetime(2010, 1, 19, 23, 0, tzinfo=tzutc())
        # should that be a real utc zoneinfo?
        # anyways, return UTC date as-is
        return date


def dt2DT(dt):
    """ Converts a python datetime object back to Zope's DateTime.

    >>> #interact(locals(), use_ipython=False )
    >>> from datetime import datetime
    >>> import pytz

    TODO: finish me.

    TODO: see, if recurrences in event browserview are datetimes or
    DateTimes. display them accordingly to the timezone of the start
    date - and not UTC

    TODO: this introduces a dependency to DateTime. move it to p.a.event.
    """
    from DateTime import DateTime
    return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.tzname())


def tzdel(dt):
    """ Create timezone naive datetime from a timezone aware one by removing
    the timezone component.

    >>> from plone.event.utils import tzdel, utctz
    >>> from datetime import datetime
    >>> dt = utctz().localize(datetime(2011, 05, 21, 12, 25))

    Remove the timezone:
    >>> tzdel(dt)
    datetime.datetime(2011, 5, 21, 12, 25)

    Using tzdel on a dt instance doesn't alter it:
    >>> dt
    datetime.datetime(2011, 5, 21, 12, 25, tzinfo=<UTC>)

    """
    if dt:
        return dt.replace(tzinfo=None)
    else:
        return None

def pydt(dt):
    """Converts a Zope's Products.DateTime in a Python datetime.

    """
    if dt is None:
        return None

    if isinstance(dt, datetime):
        tznaive = not bool(getattr(dt, 'tzinfo', False))
        if tznaive: return utctz().localize(dt)
        return utcoffset_normalize(dt, dstmode=DSTADJUST)

    tz = guesstz(dt)
    if tz is None:
        dt = dt.toZone('UTC')
        tz = utctz()

    year, month, day, hour, min, sec = dt.parts()[:6]
    # seconds (parts[6]) is a float, so we map to int
    sec = int(sec)
    # There is a problem with timezone Europe/Paris
    # tz is equal to <DstTzInfo 'Europe/Paris' PMT+0:09:00 STD>
    dt = datetime(year, month, day, hour, min, sec, tzinfo=tz)
    # before:
    # datetime.datetime(2011, 3, 14, 14, 19, tzinfo=<DstTzInfo 'Europe/Paris' PMT+0:09:00 STD>)
    # dt = dt.tzinfo.normalize(dt)
    # after: datetime.datetime(2011, 3, 14, 15, 10, tzinfo=<DstTzInfo 'Europe/Paris' CET+1:00:00 STD>
    dt = utcoffset_normalize(dt, dstmode=DSTADJUST)
    # after: datetime.datetime(2011, 3, 14, 19, tzinfo=<DstTzInfo 'Europe/Paris' CET+1:00:00 STD>
    return dt

def guesstz(DT):
    """'Guess' pytz from a zope DateTime.

    !!! theres no real good method to guess the timezone.
    DateTime was build somewhere in 1998 long before python had a working
    datetime implementation available and still stucks with this incomplete
    implementation.

    >>> from DateTime import DateTime
    >>> from plone.event.utils import guesstz

    Timezones with the same name as in the Olson DB can easily be guessed.
    >>> guesstz(DateTime('2010-01-01 Europe/Vienna'))
    <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

    GMT timezones which are popular with DateTime cannot be guessed,
    unfortunatly
    >>> guesstz(DateTime('2010-01-01 GMT+1'))
    """
    if DT.timezoneNaive():
        return utctz()
    tzname = DT.timezone()

    # In the Olson timezone database, Etc/GMT+1 seems not to be the same as
    # GMT+1. The UTC offsets are different. Therefore a conversion from GMT
    # to a pytz equivalent is not easily possible.
    #    # DateTime timezones not fully compatible with pytz
    #    # see http://pypi.python.org/pypi/DateTime
    #    if tzname.startswith('GMT'):
    #        tzname = 'Etc/%s' % tzname
    try:
        tz = pytz.timezone(tzname)
        return tz
    except KeyError:
        pass
    return None


### Date as integer representation helpers
def dt2int(dt):
    """Calculates an integer from a datetime.
    Resolution is one minute, always relative to utc

    """
    if dt is None:
        return 0
    # TODO: if dt has not timezone information, guess and set it
    dt = utc(dt)
    value = (((dt.year*12+dt.month)*31+dt.day)*24+dt.hour)*60+dt.minute

    # TODO: unit test me
    if value > MAX32:
        # value must be integer fitting in the 32bit range
        raise OverflowError(
            """%s is not within the range of indexable dates,<<
            exceeding 32bit range.""" % dt
        )
    return value

def int2dt(dtint):
    """Returns a datetime object from an integer representation with
    resolution of one minute, relative to utc.

    """
    if not isinstance(dtint, int):
        raise ValueError('int2dt expects integer values as arguments.')
    minutes = dtint % 60
    hours = dtint / 60 % 24
    days = dtint / 60 / 24 % 31
    months = dtint / 60 / 24 / 31 % 12
    years = dtint / 60 / 24 / 31 / 12
    return datetime(years, months, days, hours, minutes,
        tzinfo=pytz.timezone('UTC'))

