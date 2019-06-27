===============================
NeCTAR Dashboard
===============================

nectar-dashboard

* Free software: GPLv3+ license

Features
--------

* TODO

Local test setup
----------------

This procedure is for running a test instance of the NeCTAR dashboard on
desktop, using the NeCTAR "dev" databases and openstack services.

* Check the NeCTAR Wiki "Get the code" page.  You don't necessarily need to
  install all of that, but you do need the "basic python env setup", and
  "virtualenv".

* Clone the appropriate branch of "horizon" and "nectar-dashboard" from the
  NeCTAR-RC repos.

* Using the instructions in the NeCTAR Wiki "Dev Infrastucture" page, set up
  SSH tunnels via one of the RA boxes for the MySQL port.

  (TODO - develop alternative to a local MySQL database server.  This
  requires the creation of a fixture to populate the database OR a selective
  dump / restore from the Dev database.)

* Create a virtual env (with python 2.7) and activate it

* In the "nectar-dashboard" sandbox, run "pip install -e ."  This installs
  all of the dependencies in "requirements.txt"

* Install test dependencies "pip install -r test-requirements.txt"   

* Obtain a copy of the "local_settings.py" file (e.g. from the horizon dev
  host) and place it in "horizon/openstack_dashboard/local".

* Edit "local_settings.py" to change the database hostname and port to your
  local MySQL SSH tunnel endpoint.

* Copy the "nectar-dashboard/theme" directory tree to
  "horizon/openstack_dashboard/themes/nectar"

* Optional: dashboard plugins:

  * Find a source for "horizon/openstack_dashboard/local/enabled" tree.  (The
    problem is that this directory is in ".gitignore" ... )

  * For each referenced horizon plugin, install the version that corresponds
    to the version of horizon that you are using; e.g. if you are using
    "stable queens" horizon, use the "stable queens" versions of the plugins.

    A good place to look for version info is the Openstack releases repo:

    * https://github.com/openstack/releases/tree/master/deliverables

  * Use pip to install the plugin.  Watch that it doesn't
    do something nasty like upgrading Django to a newer version!
    (Apparently, the plugins tend to specify their dependencies too
    loosely.)

  * As an alternative to installing a plugin and its dependencies, you could
    move the plugin config out if the "enabled" tree.  (Create a "disabled" tree.)
    
* Try it out:

  * Change directory to the horizon checkout.
  * Export DJANGO_SETTINGS_MODULE=openstack_dashboard.settings
  * Run "python ./manage.py runserver 0.0.0.0:8000"
  * Point a web browser at http://127.0.0.1:8000
  * If all is well, you should get a test NeCTAR AAF login page.
  * Refer to the RC Wiki Dev page for details on how to login, etc.  Note that
    the user id you use needs to be (or at least look like) a valid email
    address, or else the Allocations plugin won't let you submit allocation
    requests, etcetera.


Policy files
------

This repository contains the OpenStack service policy files used by OpenStack
dashboard for deciding which features to allow for users.

The policy files used by OpenStack dashboard are in JSON format, rather than
the simpler YAML format now used by most OpenStack services, therefore we need
to generate new JSON policy files.

To do this, log into the dev server running the OpenStack service and activate
the virtual env.

Use oslopolicy-sample-generator to generate the config to /tmp

```
oslopolicy-sample-generator --namespace $PROJECT --format json \
    --output-file /tmp/$PROJECT_policy.json
```

The resulting policy file will be the default, so if we are running with any
policy changes in production, then these changes will need to be made in the
JSON policy file just generated.

The policy file should then be stored in this repository, and will need to be
referenced in OpenStack dashboard's local_settings.py.

For example:

```
POLICY_FILES = {
    'identity': 'keystone_policy.json',
    'compute': 'nova_policy.json',
    'volume': 'cinder_policy.json',
    'image': 'glance_policy.json',
    'network': 'neutron_policy.json',
}
```
