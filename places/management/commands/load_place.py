from django.core.management.base import BaseCommand
from places.models import Place, Image
import requests
from urllib.parse import urlparse
import os
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = 'Загружает данные о месте из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument('json_url', type=str, help='URL JSON-файла с данными о месте')

    def handle(self, *args, **options):
        json_url = options['json_url']
        
        try:
            response = requests.get(json_url)
            response.raise_for_status()
            place_data = response.json()
            
            place, created = Place.objects.update_or_create(
                title=place_data['title'],
                defaults={
                    'description_short': place_data.get('description_short', ''),
                    'description_long': place_data.get('description_long', ''),
                    'lng': place_data['coordinates']['lng'],
                    'lat': place_data['coordinates']['lat']
                }
            )
            
            place.images.all().delete()
            
            for img_url in place_data.get('imgs', []):
                image = Image(place=place)
                
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                
                img_name = os.path.basename(urlparse(img_url).path)
                
                image.image.save(
                    img_name,
                    ContentFile(img_response.content),
                    save=True
                )
                image.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Успешно создано новое место: {place.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Успешно обновлено место: {place.title}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при загрузке данных: {str(e)}'))
