from django.core.management.base import BaseCommand
from vocational.models import TimeCard


class Command(BaseCommand):
    help = 'Remove duplicate TimeCard entries based on (student, time_in, time_out)'

    def handle(self, *args, **options):
        seen = set()
        duplicates = []

        self.stdout.write("Scanning TimeCard entries for duplicates...")

        for tc in TimeCard.objects.all().order_by('id'):
            key = (tc.student_id, tc.time_in, tc.time_out)
            if key in seen:
                duplicates.append(tc.id)
            else:
                seen.add(key)

        if not duplicates:
            self.stdout.write(self.style.SUCCESS("No duplicates found."))
            return

        self.stdout.write(f"{len(duplicates)} duplicates found.")

        confirm = input("Do you want to delete them? [y/N]: ")

        if confirm.lower() == 'y':
            TimeCard.objects.filter(id__in=duplicates).delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(duplicates)} duplicate TimeCard entries."))
        else:
            self.stdout.write(self.style.WARNING("Aborted. No entries deleted."))
