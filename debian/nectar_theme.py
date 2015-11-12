import os
from openstack_dashboard.settings import HORIZON_CONFIG

NECTAR_THEME = "/usr/share/nectar-dashboard/theme"

if os.path.exists(NECTAR_THEME):
        CUSTOM_THEME_PATH = NECTAR_THEME

HORIZON_CONFIG["customization_module"] = "nectar_dashboard.overrides"
