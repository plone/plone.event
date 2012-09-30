from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from zope.component import adapts
from zope.interface import implements


class EventAccessor(object):
    """Simple event accessor adapter implementation for generic events, which
    follow the IEvent interface closely.

    Concrete implementations adapt a content type to the IEvent specification.

    """
    implements(IEventAccessor)
    adapts(IEvent)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

    def __getattr__(self, name):
        return getattr(self.context, name)

    def __setattr__(self, name, value):
        setattr(self.context, name, value)

    def __delattr__(self, name):
        delattr(self.context, name)

    @property
    def duration(self):
        return self.end - self.start
