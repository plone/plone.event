# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#
__author__ = """Jens Klein <jens@bluedynamics.com>,
                Johannes Raggam <johannes@raggam.co.at>"""

from datetime import timedelta

DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'

def utcoffset_normalize(date, delta=None, dstmode=DSTAUTO):
    """Fixes invalid UTC offsets from recurrence calculations
    @param date: datetime instance to normalize.
    @param delta: datetime.timedelta instance
    @param dstmode: is either DSTADJUST, DSTKEEP or DSTAUTO. On DSTADJUST we have a
            more human behaviour on daylight saving time changes: 8:00 on
            day before spring dst-change plus 24h results in 8:00 day after
            dst-change, which means in fact one hour less is added. On a
            recurconf.recrule < 24h this will fail!
            If DSTKEEP is selected, the time is added in its real hours, so
            the above example results in 9:00 on day after dst-change.
            DSTAUTO uses DSTADJUST for a delta >=24h and DSTKEEP for < 24h.

    """
    try:
        assert(bool(date.tzinfo))
    except:
        raise TypeError, u'Cannot normalize timezone naive dates'
    assert(dstmode in [DSTADJUST, DSTKEEP, DSTAUTO])
    if delta:
        assert(isinstance(delta, timedelta)) # Easier in Java
        delta = delta.seconds + delta.days*24*3600 # total delta in seconds
        if dstmode==DSTAUTO and delta<24*60*60:
            dstmode = DSTKEEP
        elif dstmode==DSTAUTO:
            dstmode = DSTADJUST

    if dstmode==DSTADJUST:
        return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    else: # DSTKEEP
        return date.tzinfo.normalize(date)
