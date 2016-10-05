import base64
import logging
import random
import sha

from django.contrib import messages
from django.conf import settings
from django import forms
from django import shortcuts

from keystoneclient.v3 import client as keystoneclient
from openstack_dashboard import api
from openstack_auth.user import create_user_from_token
from openstack_auth.user import set_session_from_user
from openstack_auth.user import Token as UserToken


LOG = logging.getLogger(__name__)


def credentials(request):
    # we get the email address here so that the user can see the
    passwordForm = forms.Form()
    password = ''

    if request.method == 'POST':
        passwordForm = forms.Form(request.POST)
        sys_random = random.SystemRandom()
        password = sha.sha(str(sys_random.getrandbits(256))).hexdigest()
        password = base64.encodestring(password)[:20]

        project = request.user.token.tenant['id']
        endpoint = api.keystone._get_endpoint_url(request, 'internalURL')

        api.keystone.user_update_own_password(
            request,
            settings.PASSWORD_RESET_TOKEN,
            password)

        # Reauthenticate.
        client = keystoneclient.Client(username=request.user.username,
                                       password=password,
                                       tenant_id=project,
                                       auth_url=endpoint)

        token = UserToken(client.auth_ref,
                          unscoped_token=request.user.token.unscoped_token)
        user = create_user_from_token(request, token, endpoint)
        set_session_from_user(request, user)
        messages.add_message(request, messages.INFO,
                             "Your password has been reset.")
    context = {'form': passwordForm,
               'password': password}

    return shortcuts.render(request, 'password/index.html', context)
