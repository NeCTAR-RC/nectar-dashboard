import logging
import os

import sentry_sdk

from nectar_dashboard import version


LOG = logging.getLogger(__name__)

# In the production image everything (including this plugin and
# Horizon itself) lives in site-packages, so sentry-sdk's default
# in-app detection would mark every frame as library code and ruin
# event grouping. List the namespaces we consider application code.
IN_APP_INCLUDE = [
    'nectar_dashboard',
    'horizon',
    'openstack_dashboard',
    'openstack_auth',
    'muranodashboard',
    'warre_dashboard',
    'varroa_dashboard',
    'designatedashboard',
    'heat_dashboard',
    'octavia_dashboard',
    'trove_dashboard',
    'cloudkittydashboard',
]


def _release():
    """Return "nectar-dashboard@<version>", or None if pbr can't tell.

    Returning None lets sentry-sdk fall back to the SENTRY_RELEASE
    environment variable, if set.
    """
    try:
        release = version.version_info.release_string()
    except Exception:
        return None
    return f'nectar-dashboard@{release}'


def setup(dsn=None, environment=None, traces_sample_rate=0.0):
    """Enable error reporting to GlitchTip/Sentry.

    A no-op unless a DSN is given or set in the SENTRY_DSN environment
    variable. Once enabled, the sentry-sdk default integrations report
    unhandled exceptions and ERROR level log messages. Never raises:
    this is called while Horizon exec's the local_settings.d snippets,
    and a bad DSN must not break settings loading.
    """
    dsn = dsn or os.environ.get('SENTRY_DSN')
    if not dsn:
        return False
    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=_release(),
            in_app_include=IN_APP_INCLUDE,
            # GlitchTip supports transactions; off by default
            traces_sample_rate=traces_sample_rate,
            # GlitchTip does not support sessions
            auto_session_tracking=False,
        )
    except Exception:
        LOG.exception('Sentry error reporting disabled after init error')
        return False
    LOG.debug('Sentry error reporting enabled')
    return True
