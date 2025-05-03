from django.core.management.base import BaseCommand
from products.models import Color


class Command(BaseCommand):
    help = 'Populate the Color model with predefined color options.'

    def handle(self, *args, **options):
        # Define a dictionary mapping color names to their hex codes.
        colors = {
            "White": "FFFFFF",
            "Black": "000000",
            "Red": "FF0000",
            "Green": "008000",  # A darker green; you could also use "00FF00" for lime
            "Blue": "0000FF",
            "Yellow": "FFFF00",
            "Cyan": "00FFFF",
            "Magenta": "FF00FF",
            "Silver": "C0C0C0",
            "Grey": "808080",
            "Maroon": "800000",
            "Olive": "808000",
            "Lime": "00FF00",
            "Aqua": "00FFFF",
            "Teal": "008080",
            "Navy": "000080",
            "Fuchsia": "FF00FF",
        }

        for name, hex_code in colors.items():
            # Use get_or_create to avoid duplicate entries
            color_obj, created = Color.objects.get_or_create(
                name=name,
                defaults={'hex_code': hex_code}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f"Created color: {name} with hex code {hex_code}"
                ))
            else:
                self.stdout.write(
                    f"Color '{name}' already exists with hex code {color_obj.hex_code}"
                )
