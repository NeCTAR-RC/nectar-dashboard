import logging
import os

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseServerError


LOG = logging.getLogger(__name__)


def healthcheck_middleware(get_response):

    healthcheck_path = getattr(settings, 'HEALTHCHECK_PATH', '/healthcheck')
    disable_file = getattr(settings, 'HEALTHCHECK_DISABLE_FILE', None)

    if not disable_file:
        LOG.warning('Healthcheck middleware enabled '
                    'without HEALTHCHECK_DISABLE_FILE set')

    def middleware(request):
        response = get_response(request)

        if request.path == healthcheck_path:
            if not disable_file or not os.path.exists(disable_file):
                response = HttpResponse('OK')
            else:
                LOG.info('Healthcheck disabled by file')
                response = HttpResponseServerError("DISABLED BY FILE")

        return response

    return middleware
