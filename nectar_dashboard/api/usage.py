import datetime
from operator import itemgetter

from cloudkittydashboard.api import cloudkitty as api

from nectar_dashboard.api import gnocchi


DATE_FORMAT = '%Y-%m-%d'


def get_begin_end(request):
    """Returns a begin and end date string to use for cloudkitty requests

    Returns a tuple of begin, end date string
    Defaults to 90 days ago and today
    """
    today = datetime.datetime.today()
    default_end = today.strftime(DATE_FORMAT)
    default_start = (today - datetime.timedelta(days=90)).strftime(DATE_FORMAT)

    begin = request.GET.get('begin', default_start)
    end = request.GET.get('end', default_end)

    return begin, end


def get_summary(request, resource_type=None, groupby=None, begin=None,
                end=None, detailed=False, filters={}):
    """resource_type arg is deprecated, use filters['type']
    """
    client = api.cloudkittyclient(request, version='2')
    if begin is None:
        begin, end = get_begin_end(request)

    filters['project_id'] = request.user.project_id

    groupby = request.GET.get('groupby', groupby)
    kwargs = {'begin': begin,
              'end': end,
              'filters': filters,
              'response_format': 'object',
              'limit': 1000,
              }
    if resource_type:
        kwargs['filters']['type'] = resource_type
    if groupby:
        kwargs['groupby'] = groupby
    usage_data = client.summary.get_summary(**kwargs).get('results')

    if detailed:
        total = 0
        for d in usage_data:
            rate = d.get('rate', 0)
            if rate:
                total += rate
        return {'sum': round(total, 2), 'data': usage_data}

    return usage_data


def most_used_resources(request, resource_type, begin=None, end=None):

    if resource_type == 'instance':
        data = instance_data(request)
    else:
        data = get_summary(request, resource_type, groupby='id',
                           begin=begin, end=end)

    data = sorted(data, key=itemgetter('rate'), reverse=True)
    count = 0
    most_used_data = []
    other_total = 0
    for d in data:
        if count < 5:
            most_used_data.append(
                {d.get('display_name', d.get('id')): d.get('rate')})
        else:
            other_total += d.get('rate', 0)
        count += 1
    if other_total > 0:
        most_used_data.append({'other': round(other_total, 2)})

    return {'count': count, 'data': most_used_data}


def instance_data(request):
    gnocchi_client = gnocchi.gnocchiclient(request)

    begin, end = get_begin_end(request)
    # We need to broaden our search dates for gnocchi by a day either side
    begin = datetime.datetime.strptime(begin, DATE_FORMAT)
    end = datetime.datetime.strptime(end, DATE_FORMAT)
    begin = (begin - datetime.timedelta(days=1)).strftime(DATE_FORMAT)
    end = (end + datetime.timedelta(days=1)).strftime(DATE_FORMAT)

    g_instances = gnocchi_client.resource.search(
        resource_type='instance',
        query=(f'ended_at=null or ended_at >= "{begin}"')
    )
    gnocchi_map = {i.get('id'): i for i in g_instances}

    instance_data = get_summary(request, resource_type='instance',
                                groupby='id')

    instance_attrs = ['display_name', 'availability_zone', 'flavor_name',
                      'started_at', 'ended_at']
    for i in instance_data:
        i['rate'] = round(i['rate'], 2)
        gnocchi_instance = gnocchi_map.get(i.get('id'))
        if gnocchi_instance:
            for attr in instance_attrs:
                i[attr] = gnocchi_instance.get(attr)

    return instance_data
