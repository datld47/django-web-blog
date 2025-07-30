from django import template
from django.utils.timezone import make_aware
from zoneinfo import ZoneInfo  # Python 3.9+
import datetime

register = template.Library()

# @register.filter(name='to_timezone')
@register.simple_tag
def to_timezone(value, tz_name):
    """
    Convert datetime (UTC or naive) to given timezone and return formatted string.
    """
    if not isinstance(value, datetime.datetime):
        return value

    try:
        # Nếu là datetime naive (chưa có tz), giả định là UTC
        if value.tzinfo is None:
            value = make_aware(value)  # Assume UTC

        # Đổi timezone
        target_tz = ZoneInfo(tz_name)
        local_dt = value.astimezone(target_tz)

        # Format datetime
        return local_dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        return value  # Nếu lỗi, trả về nguyên gốc