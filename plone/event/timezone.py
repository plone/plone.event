import os
import time
import pytz
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ServerTimezoneGetter(object):
    """ Retrieve the timezone from the server.

    """

    @property
    def timezone(self):
        """ Get the timezone of the server.
        Default Fallback: UTC

        >>> from zope.component import getUtility
        >>> from plone.event.interfaces import ITimezoneGetter
        >>> tzgetter = getUtility(ITimezoneGetter, 'FallbackTimezoneGetter')
        >>> import os
        >>> import time
        >>> timetz = time.tzname
        >>> ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None

        >>> os.environ['TZ'] = "Europe/Vienna"
        >>> tzgetter().timezone
        'Europe/Vienna'

        >>> os.environ['TZ'] = ""
        >>> time.tzname = None
        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...    warnings.simplefilter("always")
        ...    tzgetter().timezone
        ...    assert(len(w) == 1)
        ...    assert(issubclass(w[-1].category, RuntimeWarning))
        ...    assert("timezone" in str(w[-1].message))
        'UTC'

        >>> time.tzname = ('CET', 'CEST')
        >>> tzgetter().timezone
        'CET'

        >>> time.tzname = timetz
        >>> if ostz:
        ...     os.environ['TZ'] = ostz
        ... else:
        ...     del os.environ['TZ']

        """
        timezone = None
        if 'TZ' in os.environ.keys():
            # Timezone from OS env var
            timezone = os.environ['TZ']
        if not timezone:
            # Timezone from python time
            zones = time.tzname
            if zones and len(zones) > 0:
                timezone = zones[0]
            else:
                # Default fallback = UTC
                import warnings
                warnings.warn("Operating system's timezone cannot be found"\
                        "- using UTC.", RuntimeWarning)
                timezone = 'UTC'
        # following statement ensures, that timezone is a valid pytz zone
        return pytz.timezone(timezone).zone

# TODO: cache me
def TimezoneVocabulary(context):
    """
    >>> import zope.component
    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> tzvocab = zope.component.getUtility(IVocabularyFactory, 'TimezoneVocabulary')

    TODO: find something more breakage proof than following test
    >>> assert('Africa/Abidjan' == list(tzvocab(None))[0].value)

    TODO: make timezone source adaptable to provide vocab with commont_timezones
          or all_timezones
    """
    return SimpleVocabulary.fromValues(pytz.common_timezones)
directlyProvides(TimezoneVocabulary, IVocabularyFactory)
