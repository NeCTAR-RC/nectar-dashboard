from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import View


class CramsRedirectView(View):
    def get(self, request):
        # get the CRAMS url from settings.py
        print(settings.CRAMS_URL)
        crams_url = settings.CRAMS_URL
        return HttpResponseRedirect(crams_url)
