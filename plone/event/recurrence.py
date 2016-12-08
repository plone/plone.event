# -*- coding: utf-8 -*-
from dateutil import rrule
from plone.event.utils import DSTAUTO
from plone.event.utils import dt2int
from plone.event.utils import pydt
from plone.event.utils import tzdel
from plone.event.utils import utc
from plone.event.utils import utcoffset_normalize

import datetime
import re


# TODO: make me configurable
MAXCOUNT = 1000  # Maximum number of occurrences


def recurrence_sequence_ical(
        start,
        recrule=None,
        from_=None,
        until=None,
        count=None,
        duration=None,
):
    """Calculates a sequence of datetime objects from a recurrence rule
    following the RFC2445 specification, using python-dateutil recurrence
    rules.  The resolution of the resulting datetime objects is one second,
    since python-dateutil rrulestr doesn't support microseconds.

    :param start:   datetime or DateTime instance of the date from which the
                    recurrence sequence is calculated.
    :type start: datetime.datetime

    :param recrule: Optional string with RFC2445 compatible recurrence
                    definition, dateutil.rrule or dateutil.rruleset instances.
    :type recrule: string

    :param from_:   Optional datetime or DateTime instance of the date, to
                    limit the result within a timespan.
    :type from_: datetime.datetime

    :param until:   Optional datetime or DateTime instance of the date, until
                    the recurrence is calculated. If not given, count or
                    MAXDATE limit the recurrence calculation.
    :type until: datetime.datetime

    :param count:   Optional integer which defines the number of occurences.
                    If not given, until or MAXDATE limits the recurrence
                    calculation.
    :type count: integer

    :param duration: Optional timedelta instance, which is used to calculate
                     if a occurence datetime plus duration is within the
                     queried timerange.
    :type duration:  datetime.timedelta

    :returns: A generator which generates a sequence of datetime instances.
    :rtype: generator

    """
    # Always use python datetime objects and remove the microseconds
    start = pydt(start, exact=False)
    from_ = pydt(from_, exact=False)
    until = pydt(until, exact=False)
    tz = start.tzinfo
    start = tzdel(start)  # tznaive | start defines tz
    _from = tzdel(from_)
    _until = tzdel(until)
    if duration:
        assert (isinstance(duration, datetime.timedelta))
    else:
        duration = datetime.timedelta(0)

    if recrule:
        # TODO BUGFIX WRONG TIME DEFINITIONS
        # THIS HACK ensures, that UNTIL, RDATE and EXDATE definitions with
        # incorrect time (currently always set to 0:00 by the recurrence
        # widget) are handled correctly.
        #
        # Following fixes are made:
        # - The UNTIL date should be included in the recurrence set, as defined
        #   by RFC5545 (fix sets it to the end of the day)
        # - RDATE definitions should have the same time as the start date.
        # - EXDATE definitions should exclude occurrences on the specific date
        #   only the same time as the start date.
        # In the long term ,the recurrence widget should be able to set the
        # time for UNTIL, RDATE and EXDATE.
        t0 = start.time()  # set initial time information.
        # First, replace all times in the recurring rule with starttime
        t0str = 'T{0:02d}{1:02d}{2:02d}'.format(t0.hour, t0.minute, t0.second)
        # Replace any times set to 000000 with start time, not all
        # rrules are set by a specific broken widget.  Don't waste time
        # subbing if the start time is already 000000.
        if t0str != 'T000000':
            recrule = re.sub(r'T000000', t0str, recrule)
        # Then, replace incorrect until times with the end of the day
        recrule = re.sub(
            r'(UNTIL[^T]*[0-9]{8})T(000000)',
            r'\1T235959',
            recrule,
        )

        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in RFC2445 string
        #          dtstart is given as timezone naive time. timezones are
        #          applied afterwards, since rrulestr doesn't normalize
        #          timezones over DST boundaries
        rset = rrule.rrulestr(
            recrule,
            dtstart=start,
            forceset=True,
            ignoretz=True,
            # compatible=True # RFC2445 compatibility
        )
    else:
        rset = rrule.rruleset()
    rset.rdate(start)  # RCF2445: always include start date

    # limit
    if _from and _until:
        # between doesn't add a ruleset but returns a list
        rset = rset.between(_from - duration, _until, inc=True)
    for cnt, date in enumerate(rset):
        # Localize tznaive dates from rrulestr sequence
        date = tz.localize(date)

        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt + 1 > MAXCOUNT:
            break
        if count and cnt + 1 > count:
            break
        if from_ and utc(date) + duration < utc(from_):
            continue
        if until and utc(date) > utc(until):
            break

        yield date
    return


def recurrence_sequence_timedelta(
        start,
        delta=None,
        until=None,
        count=None,
        dst=DSTAUTO,
):
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
        if MAXCOUNT and cnt + 1 > MAXCOUNT:
            break
        if count and cnt + 1 > count:
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
