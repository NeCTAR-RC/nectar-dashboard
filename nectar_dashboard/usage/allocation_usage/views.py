import datetime
import json

from horizon import views as horizon_views

from nectar_dashboard.api import allocation as allocation_api
from nectar_dashboard.api import usage


class IndexView(horizon_views.HorizonTemplateView):

    template_name = 'allocation_usage/index.html'
    page_title = "Allocation"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        allocation = allocation_api.get_current_allocation(self.request)

        if not allocation:
            # Should never get here due to test in allowed method of panel
            raise

        context['allocation'] = allocation
        su_budget = allocation_api.get_quota(self.request, 'rating.budget')
        context['su_budget'] = su_budget
        today = datetime.datetime.today()

        total_allocation_days = (allocation.end_date
                                 - allocation.start_date).days
        day_budget = su_budget / total_allocation_days
        days_used = (today.date() - allocation.start_date).days
        on_track_usage = day_budget * days_used

        begin = allocation.start_date.strftime('%Y-%m-%d')
        end = allocation.end_date.strftime('%Y-%m-%d')
        usage_data = usage.get_summary(self.request, groupby='time-1d',
                                       begin=begin, end=end)

        cumulative = []
        total_rate = 0
        for u in usage_data:
            rate = u.get('rate')
            # In case we get a None for rate at a point
            if rate:
                total_rate += rate
            _begin = datetime.datetime.strptime(
                u.get('begin'), "%Y-%m-%dT%H:%M:%S%z").date()
            if _begin > today.date():
                cumulative.append({'begin': str(_begin), 'rate': None})
            else:
                cumulative.append({'begin': str(_begin), 'rate': total_rate})

        context['cumulative_data'] = json.dumps(cumulative)
        context['budget_tracking'] = total_rate - on_track_usage
        on_target_data = [{'begin': begin, 'rate': 0},
                          {'begin': end, 'rate': su_budget}]
        context['on_target_data'] = on_target_data

        summary_data = usage.get_summary(self.request, begin=begin, end=end)
        if summary_data:
            context['su_used'] = summary_data[0].get('rate')
            context['total_hours'] = summary_data[0].get('qty')
        else:
            context['su_used'] = 0
            context['total_hours'] = 0

        return context
