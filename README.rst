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

* Clone the appropriate branch of "horizon" and "nectar_dashboard" from the
  NeCTAR-RC repos.

* Using the instructions in the NeCTAR Wiki "Dev Infrastucture" page, set up
  SSH tunnels via one of the RA boxes for the MySQL port.

  (TODO - develop alternative to a local MySQL database server.  This
  requires the creation of a fixture to populate the database OR a selective
  dump / restore from the Dev database.)

* Create a virtual env (with python 2.7) and activate it

* In the "nectar_dashboard" sandbox, run "pip install -e ."  This installs
  all of the dependencies in "requirements.txt"

* Install test dependencies "pip install -r test-requirements.txt"   

* Obtain a copy of the "local_settings.py" file (e.g. from the horizon dev
  host) and place it in "horizon/openstack_dashboard/local".

* Edit "local_settings.py" to change the database hostname and port to your
  local MySQL SSH tunnel endpoint.

* Copy the "nectar_dashboard/theme" directory tree to
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


 
