# -*- coding: utf-8 -*-

import datetime
from dateutil import rrule
from plone.event.utils import (
        pydt, dt2int, utc, utcoffset_normalize, DSTAUTO, tzdel)

# TODO: make me configurable
MAXCOUNT = 1000  # Maximum number of occurrences


def recurrence_sequence_ical(
    start,
    recrule=None,
    from_=None,
    until=None,
    count=None
    ):

    """Calculates a sequence of datetime objects from a recurrence rule
    following the RFC2445 specification, using python-dateutil recurrence
    rules.  The resolution of the resulting datetime objects is one second,
    since python-dateutil rrulestr doesn't support microseconds.

    :param start:   datetime or DateTime instance of the date from which the
                    recurrence sequence is calculated.
    :type start: datetime

    :param recrule: String with RFC2445 compatible recurrence definition,
                    dateutil.rrule or dateutil.rruleset instances.
    :type recrule: string

    :param from_:   datetime or DateTime instance of the date, to limit -
                    possibly with until - the result within a timespan -
                    The Date Horizon.
    :type from_: datetime

    :param until:   datetime or DateTime instance of the date, until the
                    recurrence is calculated. If not given, count or MAXDATE
                    limit the recurrence calculation.
    :type until: datetime

    :param count:   Integer which defines the number of occurences. If not
                    given, until or MAXDATE limits the recurrence calculation.
    :type count: integer

    :returns: A generator which generates a sequence of datetime instances.
    :rtype: generator

    """
    # Always use python datetime objects and remove the microseconds
    start = pydt(start, microseconds=False)
    from_ = pydt(from_, microseconds=False)
    until = pydt(until, microseconds=False)
    tz = start.tzinfo
    start = tzdel(start)  # tznaive | start defines tz
    _from = tzdel(from_)
    _until = tzdel(until)

    if recrule:
        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in RFC2445 string
        #          dtstart is given as timezone naive time. timezones are
        #          applied afterwards, since rrulestr doesn't normalize
        #          timezones over DST boundaries
        rset = rrule.rrulestr(recrule,
                              dtstart=start,
                              forceset=True,
                              ignoretz=True
                              # compatible=True # RFC2445 compatibility
                              )
    else:
        rset = rrule.rruleset()
    rset.rdate(start)  # RCF2445: always include start date

    # limit
    if _from and _until:
        # between doesn't add a ruleset but returns a list
        rset = rset.between(_from, _until, inc=True)
    for cnt, date in enumerate(rset):
        # Localize tznaive dates from rrulestr sequence
        date = tz.localize(date)

        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT:
            break
        if count and cnt+1 > count:
            break
        if from_ and utc(date) < utc(from_):
            continue
        if until and utc(date) > utc(until):
            break

        yield date
    return


def recurrence_sequence_timedelta(start, delta=None, until=None, count=None,
                                  dst=DSTAUTO):
    """ Calculates a sequence of datetime objects from a timedelta integer,
    which defines the minutes between each occurence.

    :param start: datetime or DateTime instance of the date from which the
                  recurrence sequence is calculated.
    :type start: datetime

    :param delta: Integer which defines the minutes
                  between each date occurence.
    :type delta: integer

    :param until: datetime or DateTime instance of the date, until the
                  recurrence is calculated. If not given,
                  count or MAXDATE limit the recurrence calculation.
    :type until: datetime

    :param count: Integer which defines the number of occurences. If not given,
                  until or MAXDATE limits the recurrence calculation.
    :param count: integer

    :param dst:   Daylight Saving Time crossing behavior. DSTAUTO, DSTADJUST or
                  DSTKEEP. For more information, see
                  plone.event.utils.utcoffset_normalize.
    :param dst: string

    :return: A generator which generates a sequence of datetime instances.
    :rtype: generator

    """
    start = pydt(start)
    yield start

    if delta is None or delta < 1 or until is None:
        return

    until = pydt(until)

    before = start
    delta = datetime.timedelta(minutes=delta)
    cnt = 0
    while True:
        after = before + delta
        after = utcoffset_normalize(after, delta, dst)

        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT:
            break
        if count and cnt+1 > count:
            break
        if until and utc(after) > utc(until):
            break
        cnt += 1

        yield after
        before = after


def recurrence_int_sequence(sequence):
    """ Generates a sequence of integer representations from a sequence of
    dateime instances.

    :param sequence: An iterable sequence of datetime instances.
    :type sequence: iterable
    :returns: Generator of integer representations of datetime instances.
    :rtype: generator

    """
    for dt in sequence:
        yield dt2int(dt)
