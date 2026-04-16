from django.shortcuts import render
from .models import Temperature
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from decouple import AutoConfig
import datetime
from django.http import JsonResponse
import hashlib
import hmac
import time



config = AutoConfig(search_path=".")
API_SECRET = config("API_SECRET")

def index(request):
    sources = Temperature.objects.values_list('source', flat=True).distinct()
    latest_temps = {}
    for source in sources:
        latest_temp = Temperature.objects.filter(source=source).order_by('-time').first()
        if latest_temp:
            latest_temps[source] = latest_temp

    return render(request, 'index.html', {'latest_temps': latest_temps})

@csrf_exempt
def api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
    
    temp = request.POST.get("temp")
    humidity = request.POST.get("humidity")
    source = request.POST.get("source")
    timestamp = request.POST.get("timestamp")
    client_hash = request.POST.get("hash")

    if not all([temp, humidity, source, timestamp, client_hash]):
        return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)


    ts = int(timestamp)
    if abs(time.time() - ts) > 120:
        return JsonResponse({"status": "error", "message": "Timestamp expired"}, status=403)
    
    payload = f"{temp}:{humidity}:{source}:{timestamp}".encode()

    expected = hmac.new(
        API_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, client_hash):
        return JsonResponse({"status": "error", "message": "Invalid signature"}, status=403)


    Temperature.objects.create(
        temp=float(temp),
        humidity=float(humidity),
        time=datetime.datetime.now(),
        source=source
    )

    return JsonResponse({"status": "success"})

line_chart = TemplateView.as_view(template_name='linechart.html')

def line_chart_json(request):
    data_type = request.GET.get('type', 'temperature')
    minutes = int(request.GET.get('minutes', 480)) 
    
    data = {
        'labels': [],           #X axis : timestamps
        'datasets': []          #Y axis : data
    }
    
    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(minutes=minutes)
    
    temperatures = Temperature.objects.filter(
        time__gte=cutoff,
        time__isnull=False
    ).values('source', 'temp', 'humidity', 'time').order_by('time')
    
    source_data = {}
    for temp in temperatures:
        source = temp['source']
        if source not in source_data:
            source_data[source] = []
        source_data[source].append(temp)
    
    # Return empty data if no records found
    if not source_data:
        return JsonResponse(data)

    color_palette = [
        'rgba(75, 192, 192, 1)',   # Teal
        'rgba(192, 75, 75, 1)',    # Red
        'rgba(75, 192, 75, 1)',    # Green
        'rgba(192, 192, 75, 1)',   # Yellow
        'rgba(192, 75, 192, 1)',   # Magenta
        'rgba(75, 75, 192, 1)',    # Blue
        'rgba(192, 128, 75, 1)',   # Orange
        'rgba(128, 75, 192, 1)',   # Purple
        'rgba(75, 128, 192, 1)',   # Light Blue
        'rgba(192, 75, 128, 1)',   # Pink
    ]
    
    sorted_sources = sorted(source_data.keys())
    source_colors = {}
    for i, source in enumerate(sorted_sources):
        source_colors[source] = color_palette[i % len(color_palette)]
    
    default_visible_source = sorted_sources[0]

    for source, records in source_data.items():        
        if data_type == 'humidity':
            key = 'humidity'
            label_suffix = ' (Kosteus)'
        else:
            key = 'temp'
            label_suffix = ' (Lämpötila)'
        values = [r[key] for r in records]

        if not data['labels']:
            data['labels'] = [r['time'].isoformat() for r in records]
        
        dataset = {
            'label': source + label_suffix,
            'data': values,
            'borderColor': source_colors[source],
            'fill': False,
            'tension': 0.1,
            'hidden': source != default_visible_source
        }
        data['datasets'].append(dataset)

    return JsonResponse(data)


