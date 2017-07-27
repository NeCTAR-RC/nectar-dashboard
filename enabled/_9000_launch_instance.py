FEATURE = 'launch_instance'
ADD_INSTALLED_APPS = ['nectar_dashboard.launch_instance']  # without this nothing gets AUTO_DISCOVERed
ADD_ANGULAR_MODULES = ['horizon.dashboard.nectar_dashboard.launch_instance']
ADD_SCSS_FILES = ['dashboard/nectar_dashboard/launch_instance/launch_instance.scss']
AUTO_DISCOVER_STATIC_FILES = True
