# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'members'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'project'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'project'

# Python panel class of the PANEL to be added.
ADD_PANEL = \
    'nectar_dashboard.project_members.panel.Members'

# A list of applications to be added to INSTALLED_APPS.
ADD_INSTALLED_APPS = [
    'nectar_dashboard.project_members',
]
