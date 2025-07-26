import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blockwirenews.settings')

app = Celery('blockwirenews')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    'scrape-news-every-30-minutes': {
        'task': 'scraper.tasks.scrape_all_sources',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    },
    'update-crypto-prices': {
        'task': 'scraper.tasks.update_crypto_prices',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
    'cleanup-old-prices': {
        'task': 'scraper.tasks.cleanup_old_price_history',
        'schedule': crontab(hour=3, minute=0),  # Run daily at 3 AM
    },
}
