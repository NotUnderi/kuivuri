from django.shortcuts import render
from .models import Temperature
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



@csrf_exempt
def index(request):
    temps = Temperature.objects.latest("time")
    if request.method == "POST":
        print(request.POST.get("temp"))
        data = Temperature(temp=float(request.POST.get("temp")),time=datetime.datetime.now(),source=request.POST.get("source"))
        data.save()
    return render (request,'index.html',{"temps":temps})

    


class TempJsonView(BaseLineChartView):
    def get_labels(self):
        l = []
        for i in Temperature.objects.values("time"):
            l.append(i.get("time"))
        return ["Temperature"]
    
    
    def get_data(self):
        Temps = Temperature.objects.values("temp","time")
        data = [{'x':x["time"], 'y':x["temp"]} for x in Temps]
       
        return data



line_chart = TemplateView.as_view(template_name='linechart.html')

def line_chart_json(request):
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
        dataset = {
            'label': source,
            'data': [temp.temp for temp in temperatures],
            'borderColor': colors.get(source, 'rgba(0, 0, 0, 1)'),  # Default to black if source not in colors
            'fill': False,
            'tension': 0.1,
            'hidden': source != 'harri'  

        }
        if not data['labels']:
            data['labels'] = [temp.time.isoformat() for temp in temperatures]
        data['datasets'].append(dataset)

    return JsonResponse(data)


