Changelog
=========

1.0dev (unreleased)
-------------------

- Add duration parameter to recurrence_sequence_ical to include events, which
  started before the queried timerange.
  [thet]


1.0rc1 (2013-07-03)
-------------------

- Handle the case, that plone.formwidget.recurrence doesn't currently set the
  times for UNTIL, RDATE and EXDATE definitions, what lead into wrong (or
  better, unexpected) recurrence results with recurrence_sequence_ical. We now
  replace the T000000 time definitions in the recurrence string with the time
  of the start date for RDATE and EXDATE definitions and with the time of the
  end of the day for UNTIL definitions (and so including a possible occurrence
  on the UNTIL date, as defined by RFC5545).
  This bugfix should be kept in here until the recurrence widget fixes that or
  when it supports setting custom times for UNTIL, RDATE and EXDATE parts.
  [thet]


1.0b4 (2013-05-27)
------------------

- Add open_end attribute to IEventAccessor interface definition to mark events
  without a defined end time.
  [thet]

- Change of pydt signature: exact instead of microseconds and set the default
  to False.
  [thet]


1.0b3 (2013-04-24)
------------------

- Raise test coverage to 100%.
  [thet]

- Add date_to_datetime, is_date, is_datetime to plone.event.utils.
  [thet]


1.0b2 (2013-02-08)
------------------

- Package metadata updated.
  [thet]


1.0b1 (2012-10-12)
------------------

- In plone.event.utils.guesstz, don't return UTC timezone for timezoneNaive
  DateTime objects. Let the callee decide what to do with timezoneNaive
  DateTime.
  [thet]

- Remove microseconds for recurrence_sequence_ical, since python-datetime
  rrulestr does not support microseconds.
  [thet]

- Let pydt preserve microseconds when converting from Zope DateTime.
  [thet]

- Include default IEventAccessor adapter.
  [thet]

- In pydt conversion util function, test for Zope DateTime via class name.
  Return Null, if something else than a datetime or DateTime object is given.
  [thet]

- Reduce MAXCOUNT for recurrences from 100000 to 1000. Indexing unlimited
  recurrences took too long.
  [thet]

- Added dedicated timezone validator with fallback zone.
  [thet]


1.0a1 (2012-02-24)
------------------

- Initial alpha (!) release from the Plone Konferenz 2012 in Munich.
  [thet]
