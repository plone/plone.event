DSTADJUST = 'adjust'
DSTKEEP   = 'keep'
DSTAUTO   = 'auto'

MAXCOUNT  = 100000 # Maximum number of occurrences


# TODO: delta = None seems not to be possible (see code)
#       DSTADJUST for delta = None makes no sense here (first iteration where no
#       previous date is known). use then DSTAUTO
def recurrence_normalize(date, delta=None, dstmode=DSTADJUST):
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
    if delta: assert(isinstance(delta, datetime.timedelta)) # Easier in Java
    delta = delta.seconds + delta.days*24*3600 # total delta in seconds
    if dstmode==DSTAUTO and delta<24*60*60:
        dstmode = DSTKEEP
    elif dstmode==DSTAUTO:
        dstmode = DSTADJUST

    if dstmode==DSTADJUST:
        return date.replace(tzinfo=date.tzinfo.normalize(date).tzinfo)
    else: # DSTKEEP
        return date.tzinfo.normalize(date)


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

    ### Timezone normalizing and returning
    before = None
    tznaive = bool(getattr(start, 'tzinfo', False))
    for cnt, date in enumerate(rset):
        # Limit number of recurrences otherwise calculations take too long
        if MAXCOUNT and cnt+1 > MAXCOUNT: break
        if count and cnt+1 > count: break
        if until and date > until: break

        # For very first occurence which is the starting date, the timezone
        # should be correct and timezone normalizing not needed
        # For timezone naive dates there is also no need for normalizing
        if before and not tznaive:
            delta = date - before
            date = recurrence_normalize(date, delta, dst)
        yield date
        before = date
    return
