from django.http import HttpResponse
from horizon import views as horizon_views
import requests


class HomeView(horizon_views.HorizonTemplateView):

    template_name = 'dashboard_home/home.html'
    page_title = "Home"


def get_ardc_news(request):

    url = 'https://ardc.edu.au/feed/latest-articles/'
    req = requests.get(url=url)
    resp = HttpResponse(req.text, content_type=req.headers['Content-Type'])
    return resp
