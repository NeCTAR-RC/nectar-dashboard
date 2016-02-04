# Disable Floating IPs
from openstack_dashboard.dashboards.project.access_and_security import tabs
from openstack_dashboard.dashboards.project.instances import tables

# Disable Floating IPs
NO = lambda *x: False

tabs.FloatingIPsTab.allowed = NO
tables.AssociateIP.allowed = NO
tables.SimpleAssociateIP.allowed = NO
tables.SimpleDisassociateIP.allowed = NO


