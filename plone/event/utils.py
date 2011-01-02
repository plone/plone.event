# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#
__author__ = """Jens Klein <jens@bluedynamics.com>,
                Johannes Raggam <johannes@raggam.co.at>"""

import pytz
from datetime import datetime
from datetime import timedelta

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'
MAX32 = int(2**31 - 1)


### Display helpers
def isSameTime(event):
    return event.start().time == event.end().time

def isSameDay(event):
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
    >>> rfc2445dt(DateTime('2010/08/31 18:00:00 Europe/Belgrade'))
    '20100831T170000Z'

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

def foldline(s, lineLen=70):
    """ make a string folded per RFC2445 (each line must be less than 75 octets)
    This code is a minor modification of MakeICS.py, available at:
    http://www.zope.org/Members/Feneric/MakeICS/
    
    >>> from plone.event.utils import foldline
    >>> foldline('foo')
    u'foo\\n'
    
    >>> longtext = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    ...             "Vestibulum convallis imperdiet dui posuere.")
    >>> foldline(longtext)
    u'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum co\\n
    nvallis imperdiet dui posuere.\\n'

    """
    workStr = s.replace(u'\r\n', u'\n').replace(u'\r', u'\n'
        ).replace(u'\n', u'\\n')
    workStr = workStr.strip()
    numLinesToBeProcessed = len(workStr) / lineLen
    startingChar = 0
    res = u''
    while numLinesToBeProcessed >= 1:
        res = u'%s%s\n ' % (res, workStr[startingChar:startingChar + lineLen])
        startingChar += lineLen
        numLinesToBeProcessed -= 1
    return u'%s%s\n' % (res, workStr[startingChar:])


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
        if dstmode==DSTADJUST:
            return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
        else: # DSTKEEP
            return date.tzinfo.normalize(date)
    except:
        # TODO: python-datetime converts e.g RDATE:20100119T230000Z to
        # datetime.datetime(2010, 1, 19, 23, 0, tzinfo=tzutc())
        # should that be a real utc zoneinfo?
        # anyways, return UTC date as-is
        return date

def pydt(dt):
    """Converts a Zope's Products.DateTime in a Python datetime.

    TODO
    ====

    >>> #interact(locals(), use_ipython=False)
    
    Strange behavior with Brazil/East Times
    ---------------------------------------
    
    >>> from DateTime import DateTime
    >>> from plone.event.utils import pydt
    >>> pydt(DateTime('2005/07/20 18:00:00 Brazil/East'))
    datetime.datetime(2005, 7, 20, 18, 6, tzinfo=<DstTzInfo 'Brazil/East' BRT-1 day, 21:00:00 STD>)

    Well, that is weired. How comes, that Brazil pydt conversion from a
    Brazil/East time gets 6 minutes added?
    pytz uses LMT timezone for Brazil/East:
    >>> import pytz
    >>> tz = pytz.timezone("Brazil/East")
    >>> tz
    <DstTzInfo 'Brazil/East' LMT-1 day, 20:54:00 STD>
    
    After normalizing tzinfo, those 6 minutes offset is added
    >>> from datetime import datetime
    >>> dt = datetime(2005, 7, 20, 18, 0, 0, tzinfo=tz)
    >>> dt.tzinfo.normalize(dt)
    datetime.datetime(2005, 7, 20, 18, 6, tzinfo=<DstTzInfo 'Brazil/East' BRT-1 day, 21:00:00 STD>)

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
    dt = datetime(year, month, day, hour, min, sec, tzinfo=tz)
    dt = dt.tzinfo.normalize(dt) # TODO: why here normalizing in DSTKEEP mode?
    return dt

def guesstz(DT):
    """'Guess' pytz from a zope DateTime.

    !!! theres no real good method to guess the timezone.
    DateTime was build somewhere in 1998 long before python had a working
    datetime implementation available and still stucks with this incomplete
    implementation.

    """
    if DT.timezoneNaive():
        return utctz()
    tzname = DT.timezone()

    #    # DateTime timezones not fully compatible with pytz
    #    # see http://pypi.python.org/pypi/DateTime/2.12.0
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

