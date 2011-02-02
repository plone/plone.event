import os
import time
import pytz

class ServerTimezoneGetter(object):
    """ Retrieve the timezone from the server.

    """

    @property
    def timezone(self):
        """ Get the timezone of the server.
        Default Fallback: UTC

        >>> import zope.component
        >>> from plone.event.interfaces import ITimezoneGetter
        >>> tzgetter = zope.component.getUtility(ITimezoneGetter)
        >>> import os
        >>> import time
        >>> timetz = time.tzname
        >>> ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None

        >>> os.environ['TZ'] = "Europe/Vienna"
        >>> tzgetter().timezone
        <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

        >>> os.environ['TZ'] = ""
        >>> time.tzname = None
        >>> tzgetter().timezone
        <UTC>

        >>> time.tzname = ('CET', 'CEST')
        >>> tzgetter().timezone
        <DstTzInfo 'CET' CET+1:00:00 STD>

        >>> time.tzname = timetz
        >>> if ostz:
        ...     os.environ['TZ'] = ostz
        ... else:
        ...     del os.environ['TZ']

        """
        zone = None
        if 'TZ' in os.environ.keys():
            zone = os.environ['TZ']
        if not zone:
            zones = time.tzname
            if zones and len(zones) > 0:
                zone = zones[0]
            else:
                zone = 'UTC'
        return pytz.timezone(zone)
