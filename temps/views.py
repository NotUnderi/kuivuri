from django.shortcuts import render
from .models import Temperature
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView

def index(request):
    temps = Temperature.objects.all()
    return render (request,'index.html',{"temps":temps})

    


class TempJsonView(BaseLineChartView):
    def get_labels(self):
        l = []
        for i in Temperature.objects.values("time"):
            l.append(i.get("time").strftime("%s"))
        return l
    
    
    def get_data(self):
        l = []
        for i in Temperature.objects.values("temp"):
            l.append(i)
        return l



line_chart = TemplateView.as_view(template_name='linechart.html')
line_chart_json = TempJsonView.as_view()

# Create your views here.
    