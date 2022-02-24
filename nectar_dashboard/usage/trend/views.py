from horizon import views as horizon_views


class IndexView(horizon_views.HorizonTemplateView):

    template_name = 'trend/index.html'
    page_title = "Trend"
