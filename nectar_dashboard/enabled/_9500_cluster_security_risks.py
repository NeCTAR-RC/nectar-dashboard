# Adds a varroa security risks column to the magnum-ui clusters table.
# The matching REST enrichment lives in nectar_dashboard.overrides. This
# file is numbered after magnum-ui's enabled files so the column is
# appended after the ones magnum-ui registers.
FEATURE = 'cluster_security_risks'

ADD_INSTALLED_APPS = ['nectar_dashboard.cluster_risks']

AUTO_DISCOVER_STATIC_FILES = True

ADD_ANGULAR_MODULES = ['nectar.cluster-security-risks']
