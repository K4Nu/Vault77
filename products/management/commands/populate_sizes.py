# products/management/commands/populate_sizes.py

from django.core.management.base import BaseCommand
from products.models import SizeGroup, Size

class Command(BaseCommand):
    help = 'Populate sizes for each SizeGroup with predefined size options.'

    def handle(self, *args, **options):
        # Define a mapping where each SizeGroup name maps to a list of sizes.
        # For Shoes: European sizes from 30 to 48.
        # For Children Clothes: numeric sizes from 88 to 170.
        waist_sizes = [28, 30, 32, 34, 36,38]
        inseam_lengths = [30, 32, 34,36]
        size_options = {
            "Men Trousers": [f"{w}x{l}" for w in waist_sizes for l in inseam_lengths]
        }

        # Retrieve all SizeGroup instances.
        sg = SizeGroup.objects.get(name="Men Trousers")
        if sg.name in size_options:
            for size_name in size_options[sg.name]:
                size_obj, created = Size.objects.get_or_create(
                    name=size_name,
                    size_group=sg
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f"Created size '{size_name}' for SizeGroup '{sg.name}'"
                    ))
                else:
                    self.stdout.write(
                        f"Size '{size_name}' for SizeGroup '{sg.name}' already exists"
                    )
        else:
            self.stdout.write(f"No size mapping for SizeGroup: {sg.name}")

