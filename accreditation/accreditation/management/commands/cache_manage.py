"""
Cache management commands for Firestore optimization

Usage:
    python manage.py cache_stats     - View cache statistics
    python manage.py cache_clear     - Clear all caches
    python manage.py cache_warmup    - Pre-populate cache with static data
"""

from django.core.management.base import BaseCommand
from accreditation.cache_utils import (
    get_cache_stats,
    clear_all_caches,
    warmup_cache,
)
import json


class Command(BaseCommand):
    help = 'Manage Firestore cache'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['stats', 'clear', 'warmup'],
            help='Cache action to perform'
        )

    def handle(self, *args, **options):
        action = options['action']

        if action == 'stats':
            self.stdout.write(self.style.SUCCESS('Fetching cache statistics...'))
            stats = get_cache_stats()
            self.stdout.write(json.dumps(stats, indent=2))

        elif action == 'clear':
            self.stdout.write(self.style.WARNING('Clearing all Firestore caches...'))
            clear_all_caches()
            self.stdout.write(self.style.SUCCESS('✓ All caches cleared successfully'))

        elif action == 'warmup':
            self.stdout.write(self.style.SUCCESS('Warming up Firestore cache...'))
            try:
                warmup_cache()
                self.stdout.write(self.style.SUCCESS('✓ Cache warmed up successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Cache warmup failed: {e}'))
