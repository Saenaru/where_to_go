from django.db import models
import urllib.request
import os
from django.core.files import File
from tempfile import NamedTemporaryFile
from django.core.exceptions import ValidationError

class Place(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    description_short = models.TextField(blank=True, verbose_name="Краткое описание")
    description_long = models.TextField(blank=True, verbose_name="Полное описание")
    lng = models.FloatField(verbose_name="Долгота")
    lat = models.FloatField(verbose_name="Широта")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"


class Image(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="places/", blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, verbose_name="URL изображения")
    position = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.image_url and not self.image:
            try:
                response = urllib.request.urlopen(self.image_url)
                if response.status == 200:
                    img_temp = NamedTemporaryFile()
                    img_temp.write(response.read())
                    img_temp.flush()
                    
                    filename = os.path.basename(self.image_url)
                    self.image.save(filename, File(img_temp), save=False)
            except Exception as e:
                print(f"Ошибка при загрузке изображения: {e}")
        
        super().save(*args, **kwargs)

    def clean(self):
        if self.image_url:
            if not self.image_url.startswith(('http://', 'https://')):
                raise ValidationError({'image_url': 'URL должен начинаться с http:// или https://'})

    def __str__(self):
        return f"{self.position} {self.place.title}"

    class Meta:
        ordering = ["position"]
