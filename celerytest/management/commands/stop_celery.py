import sys
from celery import Celery
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Stop celery worker'

    def handle(self, *args, **options):
	celery = Celery(broker=settings.BROKER_URL)
	celery.control.broadcast("shutdown")
	self.stdout.write('All celery workers stopped\n')
