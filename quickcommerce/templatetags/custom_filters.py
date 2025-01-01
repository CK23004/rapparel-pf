from django import template
from django.utils.timezone import now

register = template.Library()

@register.filter
def can_return(placed_at):
    """Check if the order is eligible for return (within 24 hours)."""
    time_diff_in_seconds = (now() - placed_at).total_seconds()
    return time_diff_in_seconds <= 86400  # 24 hours in seconds
