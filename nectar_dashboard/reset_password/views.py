import base64
import logging
import random
import time
import sha

from django.contrib import messages
from django.conf import settings
from django import forms
from django import shortcuts

from keystoneclient.v3 import client as keystoneclient
from keystoneauth1.identity import v3
from openstack_dashboard import api
from openstack_auth import utils
from openstack_auth import user as auth_user


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

        project_id = request.user.token.tenant['id']
        endpoint, __ = utils.fix_auth_url_version_prefix(request.user.endpoint)
        session = utils.get_session()

        api.keystone.user_update_own_password(
            request,
            settings.PASSWORD_RESET_TOKEN,
            password)

        # Reauthenticate.
        auth = v3.Password(auth_url=endpoint,
                           username=request.user.username,
                           password=password,
                           project_id=project_id,
                           user_domain_id=request.user.user_domain_id,
                           project_domain_id=request.user.token.project['domain_id'])

        auth_ref = auth.get_access(session)
        token = auth_user.Token(auth_ref, unscoped_token=auth_ref.auth_token)
        user = auth_user.create_user_from_token(request, token, endpoint)
        auth_user.set_session_from_user(request, user)
        # (sorrison) This is needed for some reason, else get a 403 from keystone....
        time.sleep(5)
        messages.add_message(request, messages.INFO,
                             "Your password has been reset.")

    context = {'form': passwordForm,
               'password': password}

    return shortcuts.render(request, 'password/index.html', context)
