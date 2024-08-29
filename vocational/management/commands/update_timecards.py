from django.core.management.base import BaseCommand
from vocational.models import TimeCard  # replace with your actual app and model


class Command(BaseCommand):
    help = 'Updates week range in all timecard objects'

    def handle(self, *args, **options):
        timecards = TimeCard.objects.all()

        for timecard in timecards:
            timecard.update_week_range()
            timecard.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated week range for all timecard objects'))
