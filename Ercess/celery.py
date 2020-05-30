import os
from celery import Celery
from celery.schedules import crontab
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ercess.settings')
 
app = Celery('Ercess')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send-mail-alternate-day': {
        'task': 'dashboard.tasks.add_message_link_mail', 
        # 'schedule': crontab(hour=48)
    	# new code
    	'schedule':crontab(minute=30, hour=18)
    	# ends here ~ new code 
    },
    'send-mail-every-day': {
        'task': 'dashboard.tasks.add_feedback_message_link_mail', 
        # 'schedule': crontab(hour=24)
        # new code
        # 'schedule':crontab(minute=30, hour=16)
        'schedule':crontab(minute=30, hour=18)
        # ends here ~ new code 
    }
}

