class RCShibbolethRouter(object):
    "Route requests for the user_info model to the rcshib database"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'user_info':
            return 'rcshib'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'user_info':
            return 'rcshib'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'user_info' or \
           obj2._meta.app_label == 'user_info':
            return False
        return None

    def all0w_migration(self, db, app_label, model_name=None, **hints):
        if db == 'rcshib':
            # The schema for the 'rcshib' database is managed by
            # the rcshibboleth project.  Migrations should be done
            # on the other side.
            return False
        return None
