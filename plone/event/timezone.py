import os
import time
import pytz
from zope.interface import implements
from plone.event.interfaces import ITimezoneGetter

class ServerTimezoneGetter():
    """ Retrieve the timezone from the server.

    """
    implements(ITimezoneGetter)

    @property
    def timezone(self):
        """ Get the timezone of the server.
        Default Fallback: UTC

        >>> from plone.event.timezone import ServerTimezoneFactory
        >>> import os
        >>> import time
        >>> timetz = time.tzname
        >>> ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None

        >>> os.environ['TZ'] = "Europe/Vienna"
        >>> ServerTimezoneFactory()
        <DstTzInfo 'Europe/Vienna' CET+1:00:00 STD>

        >>> os.environ['TZ'] = None
        >>> time.tzname = None
        >>> ServerTimezoneFactory()
        <UTC>

        >>> time.tzname = ('CET', 'CEST')
        >>> ServerTimezoneFactory()
        <DstTzInfo 'CET' CET+1:00:00 STD>

        >>> time.tzname = origtz
        >>> if ostz:
        ...     os.environ['TZ'] = ostz
        ... else:
                del os.environ['TZ']

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
