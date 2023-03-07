
from django import http
from django.views.decorators import cache
from horizon import views as horizon_views
import requests

from nectar_dashboard.api import manuka


class HomeView(horizon_views.HorizonTemplateView):

    template_name = 'dashboard_home/home.html'
    page_title = "Home"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            keystone_id = self.request.user.keystone_user_id
            client = manuka.manukaclient(self.request)
            self.manuka_user = client.users.get(keystone_id)
            context['first_name'] = self.manuka_user.first_name
            context['surname'] = self.manuka_user.surname
            context['displayname'] = self.manuka_user.displayname
        except Exception:
            context['first_name'] = ""
            context['surname'] = ""
            context['displayname'] = ""

        return context


@cache.cache_page(3600)
def get_ardc_news(request):

    url = 'https://ardc.edu.au/feed/latest-articles/'
    req = requests.get(url=url)
    return http.HttpResponse(req.text,
                             content_type=req.headers['Content-Type'])
