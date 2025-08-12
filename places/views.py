from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place, Image

def place_details(request, place_id):
    place = get_object_or_404(
        Place.objects.prefetch_related('images'), 
        id=place_id
    )
    
    img_urls = [request.build_absolute_uri(img.image.url) for img in place.images.all() if img.image]
    
    return JsonResponse({
        "title": place.title,
        "imgs": img_urls,
        "description_short": place.short_description or "",
        "description_long": place.long_description or "",
        "coordinates": {
            "lng": place.lng,
            "lat": place.lat
        }
    }, json_dumps_params={'ensure_ascii': False})

def get_places_geojson(request):
    places = Place.objects.all()
    features = []
    
    for place in places:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [place.lng, place.lat]
            },
            "properties": {
                "title": place.title,
                "placeId": place.id,
                "detailsUrl": f"/place/{place.id}/"
            }
        })
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return JsonResponse(geojson_data, json_dumps_params={'ensure_ascii': False})

def home(request):
    places = Place.objects.all()
    features = []
    
    for place in places:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [place.lng, place.lat]
            },
            "properties": {
                "title": place.title,
                "placeId": place.id,
                "detailsUrl": f"/place/{place.id}/"
            }
        })
    
    geojson_data = {
        "type": "FeatureCollection", 
        "features": features
    }
    
    return render(request, 'index.html', {
        'geojson_data': geojson_data
    })