import os
from openstack_dashboard.settings import HORIZON_CONFIG

NECTAR_BASE = "/usr/share/nectar-dashboard"
NECTAR_THEME = os.path.join(NECTAR_BASE, "theme")

if os.path.exists(NECTAR_THEME):
        CUSTOM_THEME_PATH = NECTAR_THEME

HORIZON_CONFIG["customization_module"] = "nectar_dashboard.overrides"

POLICY_FILES_PATH = os.path.join(NECTAR_BASE, "policy")
