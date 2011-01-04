# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#
__author__ = """Jens Klein <jens@bluedynamics.com>,
                Johannes Raggam <johannes@raggam.co.at>"""

from zope.component import adapts
from zope.interface import implements

import datetime
from dateutil import rrule
from plone.event.utils import pydt, dt2int, utc, utcoffset_normalize, DSTAUTO
from plone.event.interfaces import IRecurringEventICal, IRecurrenceSupport

# TODO: make me configurable, somehow.
MAXCOUNT  = 100000 # Maximum number of occurrences


class RecurrenceSupport(object):
    """Recurrence support event adapter for IRecurringEvent objects.

    """
    implements(IRecurrenceSupport)
    adapts(IRecurringEventICal)

    def __init__(self, context):
        self.context = context

    def occurences_start(self):
        rset = recurrence_sequence_ical(self.context.start_date,
                                        recrule=self.context.recurrence)
        return list(rset)

    def occurences_end(self):
        rset = recurrence_sequence_ical(self.context.end_date,
                                        recrule=self.context.recurrence)
        return list(rset)

    def occurences(self):
        # TODO: is this method neccessary?
        starts = self.occurences_start()
        ends = self.occurences_end()
        events = map(
            lambda start,end:dict(
                start_date = start,
                end_date = end),
            starts, ends)
        return events


def recurrence_sequence_ical(start, recrule=None, until=None, count=None):
    """ Calculates a sequence of datetime objects from a recurrence rule
    following the RFC2445 specification, using python-dateutil recurrence rules.

    @param start:   datetime or DateTime instance of the date from which the
                    recurrence sequence is calculated.

    @param recrule: String with RFC2445 comaptible recurrence definition,
                    dateutil.rrule or dateutil.rruleset instances.

    @param until:   datetime or DateTime instance of the date, until the
                    recurrence is calculated. If not given, count or MAXDATE
                    limit the recurrence calculation.

    @param count:   Integer which defines the number of occurences. If not
                    given, until or MAXDATE limits the recurrence calculation.

    @return: A generator which generates a sequence of datetime instances.

    """
    start = pydt(start) # always use python datetime objects
    until = pydt(until)
    tz = start.tzinfo
    start = start.replace(tzinfo=None) # tznaive

    if isinstance(recrule, str):
        # RFC2445 string
        # forceset: always return a rruleset
        # dtstart: optional used when no dtstart is in RFC2445 string
        #          dtstart is given as timezone naive time. timezones are
        #          applied afterwards, since rrulestr doesn't normalize
        #          timezones over DST boundaries
        rset = rrule.rrulestr(recrule,
                              dtstart=start,
                              forceset=True,
                              # ignoretz=True
                              # compatible=True # RFC2445 compatibility
                              )
    else:
        rset = rrule.rruleset()
    rset.rdate(start) # RCF2445: always include start date 

    for cnt, date in enumerate(rset):
        # Localize tznaive dates from rrulestr sequence
        date = tz.localize(date)

        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and utc(date) > utc(until): break

        yield date
    return


def recurrence_sequence_timedelta(start, delta=None, until=None, count=None,
                                  dst=DSTAUTO):
    """ Calculates a sequence of datetime objects from a timedelta integer,
    which defines the minutes between each occurence.

    @param start: datetime or DateTime instance of the date from which the
                  recurrence sequence is calculated.

    @param delta: Integer which defines the minutes between each date occurence.

    @param until: datetime or DateTime instance of the date, until the
                  recurrence is calculated. If not given, count or MAXDATE limit
                  the recurrence calculation.

    @param count: Integer which defines the number of occurences. If not given,
                  until or MAXDATE limits the recurrence calculation.

    @param dst:   Daylight Saving Time crossing behavior. DSTAUTO, DSTADJUST or
                  DSTKEEP. For more information, see
                  plone.event.utils.utcoffset_normalize.

    @return: A generator which generates a sequence of datetime instances.

    """
    start = pydt(start)
    yield start

    if delta is None or delta < 1 or until is None: return

    until = pydt(until)

    before = start
    delta = datetime.timedelta(minutes=delta)
    cnt = 0
    while True:
        after = before + delta
        after = utcoffset_normalize(after, delta, dst)

        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and utc(after) > utc(until): break
        cnt += 1

        yield after
        before = after


def recurrence_int_sequence(sequence):
    """ Generates a sequence of integer representations from a sequence of
    dateime instances.

    """
    for dt in sequence:
        yield dt2int(dt)
