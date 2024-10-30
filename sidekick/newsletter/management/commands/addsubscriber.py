from django.core.management.base import BaseCommand
from django.utils import timezone
from sidekick.newsletter.models import Subscriber


class Command(BaseCommand):
    help = 'Create subscriber.'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument("--name", type=str)

    def handle(self, *args, **options):
        Subscriber.objects.create(
            email=options['email'],
            name=options['name'],
            subscribed=timezone.now()
        )
