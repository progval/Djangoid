#Djangoid - Django-based OpenID server/provider
#Copyright (C) 2006  Nicolas Trangez <ikke nicolast be>
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#EOL
from urllib2 import urlopen, URLError
import sha
from HTMLParser import HTMLParser, HTMLParseError

def microid(c, p):
        return sha.new(sha.new(c).hexdigest() + sha.new(p).hexdigest()).hexdigest()

class MicroIDParser(HTMLParser):
        in_head = False
        microids = []

        def handle_starttag(self, tag, attrs):
                if tag.lower() == "head":
                        self.in_head = True
                if self.in_head and tag.lower() == "meta" and self.get_attr(attrs, "name") and self.get_attr(attrs, "name").lower() == "microid":
                        self.microids.append(self.get_attr(attrs, "content"))

        def handle_endtag(self, tag):
                if tag.lower() == "head":
                        self.in_head = False

        def get_microids(self):
                return self.microids

        def get_attr(self, attrs, name):
                for a in attrs:
                        if a[0] == name:
                                return a[1]
                return None

def find_microid(uri):
        ret = None
        p = MicroIDParser()
        buffsize = 4096
        try:
                handle = urlopen(uri)
                html = handle.read(buffsize)
                while html:
                        p.feed(html)
                        html = handle.read(buffsize)
                ret = p.get_microids()
        except URLError, ue:
                pass
        except HTMLParseError, he:
                pass
        except ValueError, ve:
                pass

        return ret
