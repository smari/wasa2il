from django.core.management import BaseCommand
from babel.messages.frontend import CommandLineInterface

class Command(BaseCommand):
    def handle(self, *args, **options):
        cli = CommandLineInterface()
        cli.run("pybabel extract -F babel.cfg -o wasa2il/locale/wasa2il.pot .".split(" "))
        cli.run("pybabel update -i wasa2il/locale/wasa2il.pot -d wasa2il/locale -D django".split(" "))
