from django.apps import apps
from django.core.management.base import BaseCommand
from sidekick.contrib.notion import settings


class Command(BaseCommand):
    help = 'Sync models with Notion databases.'

    def handle(self, *args, **options):
        for dbname, dbid in settings.DATABASES.items():
            Model = apps.get_model(dbname)
            Model.objects.sync()
