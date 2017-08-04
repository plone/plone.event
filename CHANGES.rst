Changelog
=========

1.3.4 (2017-08-04)
------------------

Bug fixes:

- fix test to work with newer pytz.
  [jensens]


1.3.3 (2016-12-19)
------------------

Bug fixes:

- Update code to follow Plone styleguide.
  [gforcada]

1.3.2 (2016-11-17)
------------------

New features:

- Support Python 3.  [davisagli]


1.3.1 (2016-08-12)
------------------

Fixes:

- Use zope.interface decorator.
  [gforcada]


1.3 (2015-09-16)
----------------

- Remove unittest2 dependency.
  [gforcada]


1.2 (2015-09-09)
----------------

- Fixed ``guesstz`` test to work with old and new ``pytz`` versions.
  pytz 2014.2 and earlier say::

    <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

  and pytz 2014.3 and later say::

    <DstTzInfo 'Europe/Vienna' LMT+1:05:00 STD>

  where ``LMT`` stands for Local Mean Time.
  [maurits]


1.1 (2014-02-11)
----------------

- Fix tests, where they broke with unicode recurrence strings and unicode date
  formating strings.
  [thet]

- Make rrule munging hack only apply to RDATEs, EXDATEs and UNTILs which have
  null times, otherwise the DateRecurrenceIndex is broken for those who are
  generating RRULES using a non-broken widget. This will still result in broken
  RRULEs for some edge cases (where an RDATE is explicitly set for midnight on
  a RRULE with a DTSTART which is not), but that's better than breaking valid
  RRULES which are not generated improperly.
  This code should go into the broken widget itself or its DataManager/Field.
  [alecpm]


1.0 (2013-11-06)
----------------

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
