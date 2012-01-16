# -*- coding: utf-8 -*-

import os
import time
import pytz
import warnings
from datetime import date
from datetime import datetime
from datetime import timedelta

DSTADJUST = 'adjust'
DSTKEEP = 'keep'
DSTAUTO = 'auto'
MAX32 = int(2**31 - 1)


def default_timezone():
    """ Retrieve the timezone from the server.
        Default Fallback: UTC

        >>> from plone.event.utils import default_timezone
        >>> import os
        >>> import time
        >>> timetz = time.tzname
        >>> ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None

        >>> os.environ['TZ'] = "Europe/Vienna"
        >>> default_timezone()
        'Europe/Vienna'

        >>> os.environ['TZ'] = ""
        >>> time.tzname = None
        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...    warnings.simplefilter("always")
        ...    default_timezone()
        ...    assert(len(w) == 1)
        ...    assert(issubclass(w[-1].category, RuntimeWarning))
        ...    assert("timezone" in str(w[-1].message))
        'UTC'

        >>> time.tzname = ('CET', 'CEST')
        >>> default_timezone()
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


### Display helpers
def is_same_time(start, end, exact=False):
    """ Test if event starts and ends at same time.

    >>> from plone.event.utils import is_same_time, pydt
    >>> from datetime import datetime, timedelta

    >>> is_same_time(datetime.now(), datetime.now()+timedelta(hours=1))
    False

    >>> is_same_time(datetime.now(), datetime.now()+timedelta(days=1))
    True

    TODO: if this test fails, it might run too fast and microseconds are the
    same. Rewrite it then AND remove this msg. didn't run through yet 8|
    Exact:
    >>> is_same_time(datetime.now(), datetime.now(), exact=True)
    False

    """
    start = pydt(start).time()
    end = pydt(end).time()
    if exact:
        return start == end
    else:
        return start.hour == end.hour and start.minute == end.minute


def is_same_day(start, end):
    """ Test if event starts and ends at same day.

    >>> from plone.event.utils import is_same_day, pydt
    >>> from datetime import datetime, timedelta

    >>> is_same_day(datetime.now(), datetime.now()+timedelta(hours=1))
    True

    >>> is_same_day(datetime.now(), datetime.now()+timedelta(days=1))
    False

    >>> is_same_day(datetime(2011, 11, 11, 0, 0, 0,),
    ...             datetime(2011, 11, 11, 23, 59, 59))
    True

    Now with one localized (UTC) datetime:
    >>> is_same_day(pydt(datetime.now()), datetime.now())
    True

    TODO: tests for different localized dates.

    """
    start = pydt(start)
    end = pydt(end)
    return start.date() == end.date()


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
        assert(isinstance(delta, timedelta))  # Easier in Java
        delta = delta.seconds + delta.days*24*3600  # total delta in seconds
        if dstmode==DSTAUTO and delta<24*60*60:
            dstmode = DSTKEEP
        elif dstmode==DSTAUTO:
            dstmode = DSTADJUST

    try:
        if dstmode==DSTKEEP:
            return date.tzinfo.normalize(date)
        else:  # DSTADJUST
            return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    except:
        # TODO: python-datetime converts e.g RDATE:20100119T230000Z to
        # datetime.datetime(2010, 1, 19, 23, 0, tzinfo=tzutc())
        # should that be a real utc zoneinfo?
        # anyways, return UTC date as-is
        return date


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


def pydt(dt, missing_zone=None):
    """Converts a Zope's Products.DateTime in a Python datetime.

    @param dt: date, datetime or DateTime object
    @param missing_zone: A pytz zone to be used, if no timezone is present.

    >>> from plone.event.utils import pydt
    >>> from datetime import date, datetime
    >>> import pytz
    >>> at = pytz.timezone('Europe/Vienna')
    >>> dt = at.localize(datetime(2010,10,30))
    >>> dt
    datetime.datetime(2010, 10, 30, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)
    >>> pydt(dt)
    datetime.datetime(2010, 10, 30, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

    >>> dd = date(2010,10,30)
    >>> dd
    datetime.date(2010, 10, 30)
    >>> pydt(dd)
    datetime.datetime(2010, 10, 30, 0, 0, tzinfo=<UTC>)

    >>> from DateTime import DateTime
    >>> DT = DateTime('2011/11/11 11:11:11 GMT+1')
    >>> pydt(DT)
    datetime.datetime(2011, 11, 11, 10, 11, 11, tzinfo=<UTC>)

    >>> DT2 = DateTime('2011/11/11 11:11:11 Europe/Vienna')
    >>> DT2
    DateTime('2011/11/11 11:11:11 Europe/Vienna')
    >>> pydt(DT2)
    datetime.datetime(2011, 11, 11, 11, 11, 11, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)

    """
    if dt is None:
        return None

    if missing_zone is None:
        missing_zone = utctz()

    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day)
    if isinstance(dt, datetime):
        tznaive = not bool(getattr(dt, 'tzinfo', False))
        if tznaive:
            return missing_zone.localize(dt)
        return utcoffset_normalize(dt, dstmode=DSTADJUST)

    tz = guesstz(dt)
    if tz is None:
        dt = dt.toZone(missing_zone.zone)
        tz = missing_zone

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


def dt_from_DTstring(datestr):
    """ Return python datetime instance from a DateTime string representation.

    %Y/%m/%d %H:%M:%S TZINFO
    or
    %Y/%m/%d %H:%M:%S.%f TZINFO

    Since strptime doesn't handle pytz zones very well, we need to bypass
    this limitation.

    """
    # TODO: implement DT-string with microseconds part.
    # TODO: file a bug for strptime pytz names handling.

    start_parts = datestr.split(' ')
    start = datetime.strptime(' '.join(start_parts)[0:2], '%Y/%m/%d %H:%M:%S')
    tz = pytz.timezone(start_parts[2])
    start = tz.localize(start) # convert naive date to event's zone


def dt_to_zone(dt, tzstring):
    """ Return a datetime instance converted to the timezone given by the
    string.

    """
    return dt.astimezone(pytz.timezone(tzstring))


### RFC2445 export helpers
def rfc2445dt(dt, mode='utc', date=True, time=True):
    """ Convert a datetime or DateTime object into an RFC2445 compatible
    datetime string.

    @param dt: datetime or DateTime object to convert.

    @param mode: Conversion mode ('utc'|'local'|'float')
        Mode 'utc':   Return datetime string in UTC
        Mode 'local': Return datetime string as local
                      including a TZID component
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
    # TODO: rfc2445dt might not be necessary. drop me then.

    dt = pydt(dt)
    if mode == 'utc':
        dt = utc(dt)
    date = "%s%s%s%s" % (date and dt.strftime("%Y%m%d") or '',
                         date and time and 'T' or '',
                         time and dt.strftime("%H%M%S") or '',
                         mode=='utc' and 'Z' or '')
    if mode == 'local':
        return date, dt.tzinfo.zone
    return date
