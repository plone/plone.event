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
from plone.event.utils import pydt, dt2int, utc
from plone.event.utils import utcoffset_normalize
from plone.event.utils import DSTAUTO
from plone.event.interfaces import IRecurringEventICal, IRecurrenceSupport

MAXCOUNT  = 100000 # Maximum number of occurrences


class RecurrenceSupport(object):
    """Recurrence support for IRecurringEvent objects.
    """
    # TODO: Ensure compatibility with Archetypes based ATEvent and Dexterity
    #       based content DXEvent.

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


def recurrence_sequence_ical(start, recrule=None, until=None, count=None,
                             dst=DSTAUTO):
    """ Sequence of datetime objects from dateutil's recurrence rules
    """
    start = pydt(start) # always use python datetime objects
    until = pydt(until)

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
    for cnt, date in enumerate(rset):
        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and utc(date) > utc(until): break

        # Timezone normalizing
        # For the very first occurence, normalizing should not be needed since
        # the starting date should be correctly set.
        # TODO: check if first occurence should be normalized with DSTADJUST
        if before:
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

    until = pydt(until)

    before = start
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
