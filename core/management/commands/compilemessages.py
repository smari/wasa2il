from django.core.management import BaseCommand
from babel.messages.frontend import CommandLineInterface

class Command(BaseCommand):
    def handle(self, *args, **options):
        cli = CommandLineInterface()
        cli.run("pybabel compile -d wasa2il/locale -D django".split(" "))
