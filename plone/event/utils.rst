=======================
plone.event utils tests
=======================


utcoffset_normalize tests
=========================

Imports
    >>> from datetime import datetime
    >>> from plone.event.utils import utcoffset_normalize

Cannot normalize timezone naive dates.
    >>> utcoffset_normalize(datetime(2010,10,10,0,0))
    Traceback (most recent call last):
    ...
    TypeError: Cannot normalize timezone naive dates

Setting a timezoned date
    >>> import pytz
    >>> at = pytz.timezone('Europe/Vienna')
    >>> date = at.localize(datetime(2010,10,10,0,0))
    >>> date
    datetime.datetime(2010, 10, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

Normalizing a correct date shouldn't change it
    >>> from plone.event.utils import DSTADJUST, DSTKEEP
    >>> utcoffset_normalize(date, dstmode=DSTADJUST)
    datetime.datetime(2010, 10, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)
    >>> utcoffset_normalize(date, dstmode=DSTKEEP)
    datetime.datetime(2010, 10, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

Setting a timezoned date with incorrect UTC offset
    >>> from datetime import timedelta
    >>> date2 = date + timedelta(31)
    >>> date2
    datetime.datetime(2010, 11, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

UTC offset should be 1 hour here. This happens with recurring dates over DST
boundaries and has to be normalized - see below.

Normalizing it with DSTADJUST should correct the UTC offset and adjusting the
time in a way, that it's value will be the same as before normalizing.
    >>> utcoffset_normalize(date2, dstmode=DSTADJUST)
    datetime.datetime(2010, 11, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)

With DSTKEEP, normalizing will also keep the time as originaly set by UTC
offset - time's value will change.
    >>> utcoffset_normalize(date2, dstmode=DSTKEEP)
    datetime.datetime(2010, 11, 9, 23, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)

This should have explained the difference between DSTADJUST and DSTKEEP.
Please note, that the naming of those two daylight saving time modes are a bit
confusing. DSTKEEP will keep the time as set by UTC offset, so it's value will
change over DST boundaries. DSTADJUST will keep the same value over DST
boundaries by adjusting the UTC offset. Often DSTADJUST is the desired behavior,
e.g. your favorite radio music show will always start at the same time,
regardless of the daylight saving time.

Automatic DST mode: DSTAUTO.
Automatic decisions which DST mode (DSTADJUST or DSTKEEP) are made upon a
timedelta difference to the previous date of a recurring sequence.
DSTAUTO is the default dstmode, so we don't need to set it here.

If the difference of the previous recurrence and the current date is less than
a day, DSTKEEP is used
    >>> utcoffset_normalize(date2, delta=timedelta(seconds=3600*24-1))
    datetime.datetime(2010, 11, 9, 23, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)

Otherwise DSTADJUST is used
    >>> utcoffset_normalize(date2, delta=timedelta(seconds=3600*24))
    datetime.datetime(2010, 11, 10, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)
