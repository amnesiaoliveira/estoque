from celery import shared_task
from .views import send_critical_stock_alert

@shared_task
def check_critical_stock():
    send_critical_stock_alert()