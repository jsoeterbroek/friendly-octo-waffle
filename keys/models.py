#from django.conf import settings
#from datetime import datetime
from django.db import models
#from django.contrib.auth.models import User
#from django.utils.dateparse import parse_datetime
#from django.db.models.signals import post_save
#from django.dispatch import receiver


class Keys(models.Model):
    """ Keys model """

    key = models.CharField("key", max_length=255, unique=True, primary_key=True)
    shortkey = models.CharField("short key", max_length=8)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    environment = models.CharField("omgeving", max_length=125)
    seen = models.CharField("opgehaald", max_length=48)
    start_timestamp = models.CharField("timestamp start", max_length=48)
    end_timestamp = models.CharField("timestamp end", max_length=48)
    #region = models.CharField("region", max_length=24)
    #batch_num = models.CharField("batch_num", max_length=24)
    #batch_size = models.IntegerField("batch_size")
    #app_bundle_id = models.CharField("app_bundle_id", max_length=255)
    #verification_key_version = models.CharField("verification_key_version", max_length=6)
    #verification_key_id = models.CharField("verification_key_id", max_length=24)
    #signature_algorithm = models.CharField("signature_algorithm", max_length=24)
    num_teks = models.IntegerField('number of keys')
    #no_users = models.IntegerField('number of users')
    #padding_multiplier = models.IntegerField('padding multiplier')

    def __str__(self):
        return self.pk

    class Meta:
        verbose_name = 'Exposure Keyset'
        verbose_name_plural = 'Exposure Keysets'

class Stats(models.Model):
    """ Stats model """

    key = models.ForeignKey(Keys, on_delete=models.CASCADE)
    sum_trl_1 = models.IntegerField("sum trl 1")
    sum_trl_2 = models.IntegerField("sum trl 2")
    sum_trl_3 = models.IntegerField("sum trl 3")

    def __str__(self):
        return '{}'.format(self.key)

    class Meta:
        verbose_name = 'Statistieken'
        verbose_name_plural = 'Statistieken'
