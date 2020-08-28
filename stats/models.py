#from django.conf import settings
#from datetime import datetime
from django.db import models
#from django.contrib.auth.models import User
#from django.utils.dateparse import parse_datetime
#from django.db.models.signals import post_save
#from django.dispatch import receiver

class Stats(models.Model):

    name = models.CharField("name", max_length=250)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    keysets_total = models.IntegerField("Totaal aantal keysets")
    teks_keyset_mean = models.IntegerField("Gemiddeld aantal TEKs per keyset")
    trl_daily_dist = models.IntegerField("TRL daily dist")

    def __str__(self):
        return self.name

    class Meta:
        #managed = False
        #db_table = "pandakeys"
        verbose_name = 'Stat'
        verbose_name_plural = 'Stats'
