#!/usr/bin/env python
import sys
import os

if os.environ["PWD"][-4:] == "/bin":
        sys.path.append("../..")
else:
        sys.path.append("../")
os.environ["DJANGO_SETTINGS_MODULE"] = "djangoid.settings"

from django.conf import settings
from djangoid.microidutils import microid, find_microid
from djangoid.users.models import ClaimedUri
import datetime

def main():
        uris = ClaimedUri.objects.all()
        for uri in uris:
                id = uri.get_microid()
                try:
                        found = find_microid(uri.uri)
                except:
                        raise #for now

                uri.last_checked = datetime.datetime.now()
                uri.is_valid = (id in found)
                uri.save()

                print "Checked", uri.uri, "for", uri.user.djangouser,", result is", uri.is_valid


if __name__ == "__main__":
        main()
