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
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from djangoid.microidutils import microid

#Represent one trusted root URI. Can be shared between several users.
class TrustedRoot(models.Model):
        root = models.URLField("Trusted root URI", primary_key = True)

        def __str__(self):
                return self.root

        class Admin:
                pass

#Represent one system user, based on Django's internal user system.
class DjangoidUser(models.Model):
        #This seems not to work:
        #djangouser = models.ForeignKey(User, primary_key = True)
        #So using an ugly hack... TODO: Fixme!
        djangouser = models.CharField('Django user username', maxlength = 30, primary_key = True, help_text = "This should be the username of an existing user in the django.contrib.auth system")
        trusted_roots = models.ManyToManyField(TrustedRoot, blank = True, null = True, help_text = "URI's trusted by this user")

        def __str__(self):
                return self.djangouser

        def authenticate(self, root):
                r = TrustedRoot.objects.filter(root = root)
                if len(r) == 0: #Certainly not trusted
                        TrustedRoot(root = root).save()
                else:
                        for mr in self.trusted_roots.all():
                                if root == mr.root:
                                        return True
                return False

        class Admin:
                pass

#Identities can have attributes. These items represent one possible attribute.
class IdentityAttribute(models.Model):
        name = models.CharField("Name", maxlength = 128, help_text = "Name of the attribute. In \"openid.sreg.nickname\" this is \"nickname\"")
        title = models.CharField("Title", maxlength = 128, help_text = "Title of the attribute, as displayed to the user")
        namespace = models.CharField("Namespace", maxlength = 32, help_text = "Namespace of the attribute. In \"openid.sreg.nickname\" this is \"sreg\"")
        description = models.TextField("Description", blank = True, help_text = "Longer description of the attribute, as displayed to the user")
        regex = models.CharField("Validation regex", maxlength = 128, blank = True, help_text = "Regex the value of this field is validated upon on updates")

        def __str__(self):
                return self.namespace + "." + self.name

        class Admin:
                pass

        class Meta:
                unique_together = (("name", "namespace"),)

#This maps an attribute to a user, including a value, obviously
class UserAttribute(models.Model):
        user = models.ForeignKey(DjangoidUser, help_text = "DjangoidUser this attribute value belongs to")
        attribute = models.ForeignKey(IdentityAttribute, help_text = "Attribute of which this is the value for this user")
        value = models.TextField("Value")
        #True if this attribute's value may be displayed to all trust roots
        public = models.BooleanField("Public", help_text = "If this is true, this attribute is returned in all authentication requests, of all trust roots")
        #List of specific trust roots this attribute may be displayed to.
        #If "public" is True, this got no meaning at all
        public_for = models.ManyToManyField(TrustedRoot, blank = True, null = True, help_text = "List of all trust roots this value should be displayed to. If \"public\" is true, this list got no value")

        def __str__(self):
                return str(self.user) + ": " + str(self.attribute)

        class Admin:
                pass

        class Meta:
                #Only store an attribute once for every user
                unique_together = (("user", "attribute"),)

#A claimed webpage. This will be checked using MicroID
class ClaimedUri(models.Model):
        user = models.ForeignKey(DjangoidUser)
        uri = models.URLField()
        last_checked = models.DateTimeField(default = datetime.datetime(2006, 1, 1))
        is_valid = models.BooleanField(default = False)

        def __str__(self):
                return self.uri

        def get_contact_uri(self):
                return settings.BASE_URL + self.user.djangouser + "/"

        def get_microid(self):
                return microid(self.get_contact_uri(), self.uri)

        class Admin:
                pass

        class Meta:
                unique_together = (("user", "uri"),)
