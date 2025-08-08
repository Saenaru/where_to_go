from django.db import models
import urllib.request
import os
from django.core.files import File
from tempfile import NamedTemporaryFile
from tinymce.models import HTMLField


class Place(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description_short = models.TextField(blank=True, verbose_name="Краткое описание места")
    description_long = HTMLField(blank=True, verbose_name="Подробное описание места")
    lng = models.FloatField(verbose_name="Долгота")
    lat = models.FloatField(verbose_name="Широта")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"


class Image(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="places/")
    position = models.PositiveIntegerField(default=0, db_index=True)

    def __str__(self):
        return f"{self.position} {self.place.title}"

    class Meta:
        ordering = ["position"]
        indexes = [
            models.Index(fields=['position']),
        ]