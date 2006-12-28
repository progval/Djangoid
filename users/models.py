from django.db import models
from django.contrib import auth

class TrustedRoot(models.Model):
        root = models.URLField(primary_key = True)

        def __str__(self):
                return self.root

        class Admin:
                pass

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

class UserAttribute(models.Model):
        user = models.ForeignKey(DjangoidUser)
        attribute = models.ForeignKey(IdentityAttribute)
        value = models.TextField()
        public = models.BooleanField()
        public_for = models.ManyToManyField(TrustedRoot, blank = True, null = True)

        def __str__(self):
                return str(self.user) + ": " + str(self.attribute)

        class Admin:
                pass

        class Meta:
                unique_together = (("user", "attribute"),)
