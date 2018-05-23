from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Wasa2il Core'

    def ready(self):
        import core.signals

