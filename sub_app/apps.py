from django.apps import AppConfig


class SubAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sub_app'
    def ready(self):
        import sub_app.signals
