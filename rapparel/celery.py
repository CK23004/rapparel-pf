from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
# Set the default Django settings module for the 'celery' program
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rapparel.settings")
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
app = Celery("rapparel")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'

# Auto-discover tasks
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'run-wizapp-products-data-every-20-minutes': {
        'task': 'quickcommerce.tasks.wizapp_products_data',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes
        'args': [2],  # Pass mode=2 as an argument
    },
    # 'run-wizapp-products-data-morning-and-night': {
    #     'task': 'quickcommerce.tasks.wizapp_products_data',
    #     'schedule': crontab(hour='10,21', minute=0),  # At 10:00 AM and 9:00 PM
    #     'args': [1],  # Pass mode=1 as an argument
    # },

    #  'run-wizapp-inventory-update-25-minutes': {
    #     'task': 'quickcommerce.tasks.sync_inventory_task',
    #     'schedule': crontab(hour='10,21', minute=0),  # At 10:00 AM and 9:00 PM
    #     'args': [1],  # Default argument if needed
    # },

    'run-inventory-update-for-all-stores': {
        'task': 'quickcommerce.tasks.sync_inventory_for_all_stores',
        'schedule': crontab(minute='*/20'),  # At 10:00 AM and 9:00 PM
    },

}

@app.task(bind=True)
def sync_inventory_for_all_stores():
    from quickcommerce.models import Store
    from quickcommerce.tasks import sync_inventory_task


    stores = Store.objects.all()  # Get all stores
    mode = 2
    for store in stores:
        # Trigger inventory sync for each store by passing the store ID
        sync_inventory_task.apply_async(args=[mode, store.rapparelid])

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")