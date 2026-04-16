from django.db import models


class Temperature(models.Model):
    temp = models.FloatField(null = False, blank = False)
    humidity = models.FloatField(null = False, blank = False)
    source = models.CharField(max_length=100, null=False, blank=False)  
    time = models.DateTimeField()


    def __str__(self):
        return f"{self.source} - {self.temp}°C, {self.humidity}% at {self.time}"

