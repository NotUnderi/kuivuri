from django.shortcuts import render
from .models import Temperature
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from chartjs.views.lines import BaseLineChartView
from decouple import AutoConfig
import os
import datetime
from django.http import JsonResponse
from pathlib import Path
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

class TempJsonView(BaseLineChartView):
    def get_labels(self):
        l = []
        for i in Temperature.objects.values("time"):
            l.append(i.get("time"))
        return ["Temperature"]
    
    
    def get_data(self):
        Temps = Temperature.objects.values("temp","time")
        Humidities = Temperature.objects.values("humidity","time")
        data = [{'x':x["time"], 'y':x["temp"]} for x in Temps]
       
        return data



line_chart = TemplateView.as_view(template_name='linechart.html')

def line_chart_json(request):
    data_type = request.GET.get('type', 'temperature')
    sources = Temperature.objects.values_list('source', flat=True).distinct()
    data = {
        'labels': [],
        'datasets': []
    }

    colors = {
        'harri': 'rgba(75, 192, 192, 1)',
        'esp8266': 'rgba(192, 75, 75, 1)'
    }

    for source in sources:
        temperatures = Temperature.objects.filter(source=source).order_by('time')
        
        # Select data based on type
        if data_type == 'humidity':
            values = [temp.humidity for temp in temperatures]
            label_suffix = ' (Humidity)'
        else:
            values = [temp.temp for temp in temperatures]
            label_suffix = ' (Temp)'
        
        dataset = {
            'label': source + label_suffix,
            'data': values,
            'borderColor': colors.get(source, 'rgba(0, 0, 0, 1)'),  # Default to black if source not in colors
            'fill': False,
            'tension': 0.1,
            'hidden': source != 'harri'  

        }
        if not data['labels']:
            data['labels'] = [temp.time.isoformat() for temp in temperatures]
        data['datasets'].append(dataset)

    return JsonResponse(data)


