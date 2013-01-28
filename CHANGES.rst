Changelog
=========

1.0dev (unreleased)
-------------------

- Nothing changed yet.


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