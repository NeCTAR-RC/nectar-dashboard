================
NeCTAR Dashboard
================

nectar-dashboard

* Free software: GPLv3+ license

Features
--------

* TODO

Local test setup
----------------

The current recommendation for setting up a local test of Horizon + the
Nectar Dashboard plugin + others is to the "dashboard-dev" project at
https://github.com/NeCTAR-RC/dashboard-dev .

Instructions are in the project's README.


Policy files
------------

This repository contains the OpenStack service policy files used by OpenStack
dashboard for deciding which features to allow for users.

The policy files used by OpenStack dashboard are in JSON format, rather than
the simpler YAML format now used by most OpenStack services, therefore we need
to generate new JSON policy files.

To do this, log into the dev server running the OpenStack service and activate
the virtual env.

Use oslopolicy-sample-generator to generate the config to /tmp::

  $ oslopolicy-sample-generator --namespace $PROJECT --format json \
    --output-file /tmp/$PROJECT_policy.json

The resulting policy file will be the default, so if we are running with any
policy changes in production, then these changes will need to be made in the
JSON policy file just generated.

The policy file should then be stored in this repository, and will need to be
referenced in OpenStack dashboard's local_settings.py.

For example::

  POLICY_FILES = {
    'identity': 'keystone_policy.json',
    'compute': 'nova_policy.json',
    'volume': 'cinder_policy.json',
    'image': 'glance_policy.json',
    'network': 'neutron_policy.json',
  }
