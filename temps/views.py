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
        data = Temperature(temp=float(request.POST.get("temp")),time=datetime.datetime.now())
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
    temperatures = Temperature.objects.all().order_by('time')
    data = {
        "labels": [temp.time.isoformat() for temp in temperatures],
        "datasets": [{
            "label": "Temperature",
            "data": [temp.temp for temp in temperatures],
            "fill": False,
            "borderColor": "rgba(75, 192, 192, 1)",
            "tension": 0.1
        }]
    }
    return JsonResponse(data)

# Create your views here.