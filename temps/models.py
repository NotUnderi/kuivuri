from django.db import models


class Temperature(models.Model):
    temp = models.FloatField()
    time = models.DateTimeField()

