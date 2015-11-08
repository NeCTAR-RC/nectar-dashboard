import horizon

# Disable Floating IPs
from openstack_dashboard.dashboards.project.access_and_security import tabs
from openstack_dashboard.dashboards.project.instances import tables

NO = lambda *x: False

tabs.FloatingIPsTab.allowed = NO
tables.AssociateIP.allowed = NO
tables.SimpleAssociateIP.allowed = NO
tables.SimpleDisassociateIP.allowed = NO


project = horizon.get_dashboard("project")
network_panel = project.get_panel("networks")
network_topology_panel = project.get_panel("network_topology")
project.unregister(network_panel.__class__)
project.unregister(network_topology_panel.__class__)
