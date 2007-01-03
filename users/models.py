from django.db import models
from django.contrib import auth

#Represent one trusted root URI. Can be shared between several users.
class TrustedRoot(models.Model):
        root = models.URLField(primary_key = True)

        def __str__(self):
                return self.root

        class Admin:
                pass

#Represent one system user, based on Django's internal user system.
class DjangoidUser(models.Model):
        #This seems not to work:
        #djangouser = models.ForeignKey(auth.models.User, primary_key = True)
        #So using an ugly hack... TODO: Fixme!
        djangouser = models.CharField('username', maxlength = 30, primary_key = True)
        trusted_roots = models.ManyToManyField(TrustedRoot, blank = True, null = True)

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
        name = models.CharField(maxlength = 128)
        namespace = models.CharField(maxlength = 32)
        description = models.TextField(blank = True)

        def __str__(self):
                return self.namespace + "." + self.name

        class Admin:
                pass

        class Meta:
                unique_together = (("name", "namespace"),)

#This maps an attribute to a user, including a value, obviously
class UserAttribute(models.Model):
        user = models.ForeignKey(DjangoidUser)
        attribute = models.ForeignKey(IdentityAttribute)
        value = models.TextField()
        #True if this attribute's value may be displayed to all trust roots
        public = models.BooleanField()
        #List of specific trust roots this attribute may be displayed to.
        #If "public" is True, this got no meaning at all
        public_for = models.ManyToManyField(TrustedRoot, blank = True, null = True)

        def __str__(self):
                return str(self.user) + ": " + str(self.attribute)

        class Admin:
                pass

        class Meta:
                #Only store an attribute once for every user
                unique_together = (("user", "attribute"),)
