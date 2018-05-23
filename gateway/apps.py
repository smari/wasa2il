from django.apps import AppConfig

class IcePirateGatewayConfig(AppConfig):
    name = 'gateway'
    verbose_name = 'IcePirate Gateway'

    def ready(self):
        import gateway.signals

