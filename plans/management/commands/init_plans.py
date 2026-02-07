"""Создание тарифов в БД при первом запуске."""

from django.core.management.base import BaseCommand

from plans.models import Plan


class Command(BaseCommand):
    help = 'Создать или обновить тарифы FREE и PRO в БД'

    def handle(self, *args, **options):
        # FREE тариф
        Plan.objects.update_or_create(
            name=Plan.FREE,
            defaults={
                'price_rub': 0,
                'duration_days': 0,
                'limits': {
                    'conversions_per_day': 3,
                    'max_file_size_mb': 25,
                    'available_formats': 'all',
                }
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Тариф {Plan.FREE} создан/обновлён'))

        # PRO тариф
        Plan.objects.update_or_create(
            name=Plan.PRO,
            defaults={
                'price_rub': 299,
                'duration_days': 30,
                'limits': {
                    'conversions_per_day': 100,
                    'max_file_size_mb': 1024,
                    'available_formats': 'all',
                }
            },
        )
        self.stdout.write(self.style.SUCCESS(f'Тариф {Plan.PRO} создан/обновлён'))

        self.stdout.write(self.style.SUCCESS('Все тарифы инициализированы'))
