# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#
__author__ = """Jens Klein <jens@bluedynamics.com>,
                Johannes Raggam <johannes@raggam.co.at>"""

import datetime
from dateutil import rrule
from Products.DateRecurringIndex.utils import pydt, dt2int, utc
from plone.event.utils import utcoffset_normalize
from plone.event.utils import DSTAUTO

MAXCOUNT  = 100000 # Maximum number of occurrences


def recurrence_sequence_ical(start, recrule=None, until=None, count=None,
                             dst=DSTAUTO):
    """ Sequence of datetime objects from dateutil's recurrence rules
    """
    # TODO: that's catched anyways when comparing both vars. Maybe leave out.
    if until:
        try:
            # start.tzinfo xnor until.tzinfo. both present or missing
            assert(not(bool(start.tzinfo) ^ bool(until.tzinfo)))
        except:
            raise TypeError, u'Timezones for both until and start have to be' \
                             + u'present or missing'

    if isinstance(recrule, rrule.rrule):
        rset = rrule.rruleset()
        rset.rrule(recrule) # always use an rset
    elif isinstance(recrule, rrule.rruleset):
        rset = recrule
    elif isinstance(recrule, str):
        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in RFC2445 string
        rset = rrule.rrulestr(recrule,
                             dtstart=start,
                             forceset=True
                             # compatible=True # RFC2445 compatibility
                             )

    rset.rdate(start) # RCF2445: always include start date

    before = None
    tznaive = not bool(getattr(start, 'tzinfo', False))
    for cnt, date in enumerate(rset):
        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and utc(date) > utc(until): break

        # Timezone normalizing
        # For the very first occurence, normalizing should not be needed since
        # the starting date should be correctly set. For timezone naive dates
        # there is also no need for normalizing
        # TODO: check if first occurence should be normalized with DSTADJUST
        if before and not tznaive:
            delta = date - before
            date = utcoffset_normalize(date, delta, dst)
        yield date
        before = date
    return


def recurrence_sequence_timedelta(start, delta=None, until=None, count=None,
                                  dst=DSTAUTO):
    """a sequence of integer objects.

    @param recurconf.start: a python datetime (non-naive) or Zope DateTime.
    @param recurconf.recrule: Timedelta as integer >=0 (unit is minutes) or None.
    @param recurconf.until: a python datetime (non-naive) or Zope DateTime >=start or None.
    @param recurconf.dst: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
                more human behaviour on daylight saving time changes: 8:00 on
                day before spring dst-change plus 24h results in 8:00 day after
                dst-change, which means in fact one hour less is added. On a
                recurconf.recrule < 24h this will fail!
                If DSTKEEP is selected, the time is added in its real hours, so
                the above example results in 9:00 on day after dst-change.
                DSTAUTO uses DSTADJUST for a delta >=24h and DSTKEEP for < 24h.

    @return: a sequence of dates
    """
    start = pydt(start)
    yield start

    if delta is None or delta < 1 or until is None: return

    before = start
    until = pydt(until)
    delta = datetime.timedelta(minutes=delta)
    cnt = 0
    while True:
        after = before + delta
        after = utcoffset_normalize(after, delta, dst)

        # TODO: can these break conditions be generalized into a function, so
        #       that it can be used with ical code?
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and utc(after) > utc(until): break
        cnt += 1

        yield after
        before = after


def recurrence_int_sequence(sequence):
    """ IRecurringSequence as integer represetations of dates.
    """
    for dt in sequence:
        yield dt2int(dt)
