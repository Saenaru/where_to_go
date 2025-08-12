from django.core.management.base import BaseCommand
from places.models import Place, Image
import requests
from urllib.parse import urlparse
import os
from django.core.files.base import ContentFile
from requests.exceptions import RequestException
from django.db.utils import IntegrityError, DataError
from django.core.files.base import File


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
            
            coordinates = place_data.get('coordinates') or {}
            lng = coordinates.get('lng') or place_data.get('lng')
            lat = coordinates.get('lat') or place_data.get('lat')
            
            try:
                place, created = Place.objects.update_or_create(
                    title=place_data['title'],
                    defaults={
                        'short_description': place_data.get('description_short', '') or place_data.get('short_description', ''),
                        'long_description': place_data.get('description_long', '') or place_data.get('long_description', ''),
                        'lng': lng,
                        'lat': lat
                    }
                )
            except (IntegrityError, DataError) as e:
                self.stdout.write(self.style.ERROR(f'Ошибка создания/обновления места: {str(e)}'))
                return
            
            if 'imgs' in place_data:
                self._process_images(place, place_data['imgs'])
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Успешно создано новое место: {place.title}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Успешно обновлено место: {place.title}'))
                
        except RequestException as e:
            self.stdout.write(self.style.ERROR(f'Ошибка загрузки JSON: {str(e)}'))
        except (ValueError, KeyError) as e:
            self.stdout.write(self.style.ERROR(f'Ошибка формата JSON: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Неожиданная ошибка: {str(e)}'))
            raise

    def _process_images(self, place, image_urls):
        place.images.all().delete()
        
        for position, img_url in enumerate(image_urls, start=1):
            try:
                img_response = requests.get(img_url)
                img_response.raise_for_status()
            except RequestException as e:
                self.stdout.write(self.style.WARNING(f'Ошибка загрузки изображения {img_url}: {str(e)}'))
                continue
            
            try:
                img_name = os.path.basename(urlparse(img_url).path)
                content_img = ContentFile(img_response.content, name=img_name)
                
                Image.objects.create(
                    place=place,
                    image=content_img,
                    position=position
                )
                self.stdout.write(f'Добавлено изображение: {img_name}')
            except (IntegrityError, DataError) as e:
                self.stdout.write(self.style.WARNING(f'Ошибка сохранения изображения {img_url}: {str(e)}'))
            except File.DoesNotExist as e:
                self.stdout.write(self.style.WARNING(f'Файл изображения не найден {img_url}: {str(e)}'))