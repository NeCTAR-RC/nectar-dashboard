# Disable Floating IPs
from openstack_dashboard.dashboards.project.access_and_security import tabs
from openstack_dashboard.dashboards.project.instances import tables
from openstack_dashboard.dashboards.project.instances import views
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import LaunchInstance
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import SelectProjectUser
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import SetInstanceDetails
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import SetAccessControls
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import CellSelection
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import PostCreationStep
from openstack_dashboard.dashboards.project.instances.workflows.create_instance import SetAdvanced

# Disable Floating IPs
NO = lambda *x: False

tabs.FloatingIPsTab.allowed = NO
tables.AssociateIP.allowed = NO
tables.SimpleAssociateIP.allowed = NO
tables.SimpleDisassociateIP.allowed = NO


# Remove SetNetwork tab from launch instance
class NeCTARLaunchInstance(LaunchInstance):
    default_steps = (SelectProjectUser,
                     SetInstanceDetails,
                     SetAccessControls,
                     CellSelection,
                     PostCreationStep,
                     SetAdvanced)

views.LaunchInstanceView.workflow_class = NeCTARLaunchInstance
