Problems with the python-dateutil package
=========================================

python-dateutil is used for all recurrence calculations in plone.app.event
(PLIP10886). It is insanely flexible, but it does not implement every bit of the
iCalendar (RFC2445 or the newer RFC5545) specification. The limitations

Our workaround to this limitations is, that we do all calculations with
python-dateutil with timezone-naive dates and convert them to the correct
timezone afterwards.

Related to this, we do not support the case, where the time should be fixed
over DST changes, like "Go for a beer every day at 6:00 PM". The time is always
adjusted, which is technically correct. With this in mind, people can work
around it by using a different content item for events after a DST change.

For reference, see: https://bugs.launchpad.net/dateutil/+bug/890196
                    https://bugs.launchpad.net/dateutil/+bug/890197

1) Why we should let rrule calculate Timezone naive dates and applyingtimezones to the sequence afterwards
==========================================================================================================

dateutil does not normalize/adjust the timezone over Daylight Saving Time
boundaries. E.g. in Austria in 2010, dst change from summertime (UTC+2) to
standard time (UTC+1) happened on 2010-10-31 at 3:00 in the morning.
dateutil gives us::

    >>> from datetime import datetime
    >>> import pytz
    >>> at = pytz.timezone('Europe/Vienna')
    >>> start = at.localize(datetime(2010,10,30))
    >>> recrule = """RRULE:FREQ=DAILY;INTERVAL=1;COUNT=3"""
    >>> from dateutil import rrule
    >>> list(rrule.rrulestr(recrule, dtstart=start))
    [datetime.datetime(2010, 10, 30, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 10, 31, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 11, 1, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)]

Note, that for 1st November, the UTC offset is wrong.
This issue is corrected by plone.event.util.utcoffset_normalize:

::

    >>> from plone.event.recurrence import recurrence_sequence_ical
    >>> list(recurrence_sequence_ical(start, recrule=recrule))
    [datetime.datetime(2010, 10, 30, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 10, 31, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 11, 1, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)]


It's safer to let rrule calculate timezone naive dates and localizing them
afterwards than letting rrule substracting (EXDATE) timezone correct dates from
a possibly timezone incorrect recurrence sequence. This issue will be gone, if
rrule does TZ normalizing itself before applying EXDATE to the recurrence
sequence.

See here... This is our recurrence rule. We want to substract from the sequence
the date 2010-10-31, 23:30 in UTC, which is 2010-11-01, 0:30 in Austria, UTC+1

::

    >>> recrule = """RRULE:FREQ=DAILY;INTERVAL=1;COUNT=3
    ...              EXDATE:20101031T233000Z"""

If we let the sequence start from 1st November, the 1st November is correctly
substracted, since the sequence has all correct timezones.

::

    >>> start = at.localize(datetime(2010, 11, 1, 0, 30))
    >>> list(rrule.rrulestr(recrule, dtstart=start, forceset=True))
    [datetime.datetime(2010, 11, 2, 0, 30, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>),
        datetime.datetime(2010, 11, 3, 0, 30, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)]

But if we start from 30th October, where UTC+2 offset is still active, the
sequence has incorrect timezones and substracting does not work as expected
anymore.

::

    >>> start = at.localize(datetime(2010,10,30,0,30))
    >>> list(rrule.rrulestr(recrule, dtstart=start, forceset=True))
    [datetime.datetime(2010, 10, 30, 0, 30, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 10, 31, 0, 30, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>),
        datetime.datetime(2010, 11, 1, 0, 30, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)]



2) python-dateutil does not accept VALUE parameter to distinguish between dateand datetime in date components
=============================================================================================================

General imports used in here::

    >>> from datetime import datetime
    >>> import pytz
    >>> at = pytz.timezone('Europe/Vienna')


Using the VALUE parameter in DTSTART or any other date component does not work.
The value parameter can be used to distinguish between DATE and DATE-TIME.
Please note, that DATE-TIME is the default.
The result is an empty list.

::

    >>> start = at.localize(datetime(2010, 1, 1, 0, 0))
    >>> recrule = """DTSTART;VALUE=DATE:20101029"""
    >>> list(rrule.rrulestr(recrule, dtstart=start, forceset=True))
    []


3) python-dateutil does not accept Timezone identifiers for Date components
===========================================================================

General imports used in here::

    >>> from datetime import datetime
    >>> import pytz
    >>> at = pytz.timezone('Europe/Vienna')


Mixing timezone aware and naive dates also breaks (this is not a bug)::

    >>> start=at.localize(datetime(2010, 1, 1, 0, 0))
    >>> recrule="""RRULE:FREQ=DAILY;INTERVAL=1;UNTIL=20100104T000000"""
    >>> list(rrule.rrulestr(recrule, dtstart=start, forceset=True))
    Traceback (most recent call last):
    ...
    ValueError: RRULE UNTIL values must be specified in UTC when DTSTART is timezone-aware


python-dateutils parse function accepts a default value, from which missing
parameters are copied. Could this be the key to solve the problem with missing
timezones?

::

    >>> from dateutil import parser

    >>> ref = at.localize(datetime(2010,1,1))
    >>> parser.parse('20100109T000000', default=ref)
    datetime.datetime(2010, 1, 9, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)


yo! but not really the solution yet. timezones are not adjusted properly
(should be CET+2 here)::

    >>> parser.parse('20100809T000000', default=ref)
    datetime.datetime(2010, 8, 9, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>)


this works. but can't be used to solve rrulestr parsing problems.

::

    >>> parser.parse('20100109T000000', default=ref.tzinfo.localize(parser.parse('20100809T000000')))
    datetime.datetime(2010, 1, 9, 0, 0, tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>)

