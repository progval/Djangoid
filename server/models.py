from django.db import models

class OidStoreNonce(models.Model):
        nonce = models.CharField(maxlength = 8, primary_key = True)
        expires = models.IntegerField()

        class Admin:
                pass

class OidStoreAssociation(models.Model):
        server_url = models.TextField()
        handle = models.CharField(maxlength = 255)
        secret = models.TextField()
        issued = models.IntegerField()
        lifetime = models.IntegerField()
        assoc_type = models.CharField(maxlength = 64)

        class Admin:
                pass

        class Meta:
                unique_together = (("server_url", "handle"),)

class OidStoreSetting(models.Model):
        setting = models.CharField(maxlength = 128, primary_key = True)
        value = models.TextField()

        class Admin:
                pass
