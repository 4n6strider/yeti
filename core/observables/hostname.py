from __future__ import unicode_literals

import re

import idna
from core.database.fields import BooleanField, StringField
from tldextract import extract

from core.observables import Observable
from core.helpers import refang
from core.errors import ObservableValidationError


class Hostname(Observable):

    # TODO: Use a smarter regex
    regex = r"((.+\.)(.+))\.?"

    domain = BooleanField()
    idna = StringField()

    DISPLAY_FIELDS = Observable.DISPLAY_FIELDS + [("domain", "Domain?"), ("idna", "IDNA")]

    def clean(self):
        """Performs some normalization on hostnames before saving to the db"""
        try:
            self.normalize(self.value)
        except Exception:
            raise ObservableValidationError("Invalid hostname: {}".format(self.value))

    def normalize(self, hostname):
        hostname = Hostname.check_type(hostname)
        if not hostname:
            raise ObservableValidationError("Invalid Hostname (check_type={}): {}".format(Hostname.check_type(hostname), hostname))
        self.value = unicode(hostname.lower())
        try:
            self.idna = unicode(idna.encode(hostname.lower()))
        except idna.core.InvalidCodepoint:
            pass

    @staticmethod
    def check_type(txt):
        hostname = refang(txt.lower())
        if hostname:
            match = re.match("^" + Hostname.regex + "$", hostname)
            if match:
                if hostname.endswith('.'):
                    hostname = hostname[:-1]

                parts = extract(hostname)
                if parts.suffix and parts.domain:
                    return hostname

        return False
