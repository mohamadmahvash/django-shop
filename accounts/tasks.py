from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from accounts.models import OtpCode


@shared_task
def remove_expired_otp_codes():
    expired_time = timezone.now() - timedelta(minutes=2)
    OtpCode.objects.filter(created_at__lte=expired_time).delete()
