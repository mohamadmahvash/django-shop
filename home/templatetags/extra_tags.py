from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def divide_thousand(value):
    prices = (
        (value // 1000000, "میلیون تومان"),
        (value // 1000, "هزار تومان"),
    )
    for price, unit in prices:
        if price >= 1:
            return f"{price:.0f} {unit}"
    return f"{value} تومان"


@register.filter
def timesince_fa(value, default='همین الان'):
    now = timezone.now()
    diff = now - value
    periods = (
        (diff.days / 365, "سال"),
        (diff.days / 30, "ماه"),
        (diff.days / 7, "هفته"),
        (diff.days, "روز"),
        (diff.seconds / 3600, "ساعت"),
        (diff.seconds / 60, "دقیقه"),
        (diff.seconds, "ثانیه"),
    )

    for period, unit in periods:
        if period >= 1:
            return f"{period:.0f} {unit}  قبل"
    return default
