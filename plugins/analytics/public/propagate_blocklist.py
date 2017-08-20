from __future__ import unicode_literals
from datetime import timedelta

from core.analytics import ScheduledAnalytics
from mongoengine import Q


class PropagateBlocklist(ScheduledAnalytics):

    default_values = {
        "frequency": timedelta(hours=1),
        "name": "PropagateBlocklist",
        "description": "Propagates blocklist from URLs to hostnames",
    }

    ACTS_ON = 'Url'  # act on Urls only

    CUSTOM_FILTER = {"tags__name": "blocklist"}  # filter only tagged elements

    EXPIRATION = None

    @staticmethod
    def each(obj):
        n = obj.neighbors(neighbor_type="Hostname").values()
        if n:
            for link in n[0]:
                link[1].tag('blocklist')
        else:
            h = ScheduledAnalytics.get(name="ProcessUrl").each(obj)
            h.tag('blocklist')
