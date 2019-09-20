# The slug of the panel to be added to HORIZON_CONFIG. Required.
PANEL = 'projects'
# The slug of the dashboard the PANEL associated with. Required.
PANEL_DASHBOARD = 'identity'
# The slug of the panel group the PANEL is associated with.
PANEL_GROUP = 'default'

# This was the default panel, but we disabled it and use app creds instead.
DEFAULT_PANEL = 'application_credentials'

# If set to True, the panel will be removed from PANEL_DASHBOARD/PANEL_GROUP.
REMOVE_PANEL = True
