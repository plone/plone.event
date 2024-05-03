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

    :param count:   Optional integer which defines the number of occurrences.
                    If not given, until or MAXDATE limits the recurrence
                    calculation.
    :type count: integer

    :param duration: Optional timedelta instance, which is used to calculate
                     if a occurrence datetime plus duration is within the
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
        assert isinstance(duration, datetime.timedelta)
    else:
        duration = datetime.timedelta(0)

    if recrule:
        # The event's start time.
        t0 = start.time()
        # The event's start time as RFC8601 string
        t0str = f"T{t0.hour:02d}{t0.minute:02d}{t0.second:02d}"

        # 1) Remove DTSTART from the recurrence rule
        # The start date is always included and therefore removed from the
        # recurrence rule.
        recrule = re.sub(r"DTSTART:[^;\n]*[;\n]", "", recrule, re.MULTILINE)

        # 2) Set all RDATE (actually any) time definitions to the start date of
        # the event, except for those explicitly set to 00:00:00 which might
        # come from recurrence rule widgets which explicitly set it to that
        # time.
        if t0str != "T000000":
            recrule = re.sub(r"T000000", t0str, recrule)

        # 3) Set the UNTIL times to the end of the day to make sure to include
        # any possible occurrence on that date.
        recrule = re.sub(
            r"(UNTIL[^T]*[0-9]{8})T([0-9]{6})(Z?)",
            r"\1T235959\3",
            recrule,
        )

        # 4) Set the EXDATE properties to the same start time as the event's
        # start time to make sure to really exclude those occurrences.
        recrule = re.sub(
            r"EXDATE:([^\n\s]+)",
            lambda m: re.sub(
                r"T[0-9]{6}(Z?)",
                rf"{t0str}\1",
                m.group(0),
            ),
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
    """Calculates a sequence of datetime objects from a timedelta integer,
    which defines the minutes between each occurrence.

    :param start: datetime or DateTime instance of the date from which the
                  recurrence sequence is calculated.
    :type start: datetime

    :param delta: Integer which defines the minutes
                  between each date occurrence.
    :type delta: integer

    :param until: datetime or DateTime instance of the date, until the
                  recurrence is calculated. If not given,
                  count or MAXDATE limit the recurrence calculation.
    :type until: datetime

    :param count: Integer which defines the number of occurrences. If not given,
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
    """Generates a sequence of integer representations from a sequence of
    dateime instances.

    :param sequence: An iterable sequence of datetime instances.
    :type sequence: iterable
    :returns: Generator of integer representations of datetime instances.
    :rtype: generator

    """
    for dt in sequence:
        yield dt2int(dt)
