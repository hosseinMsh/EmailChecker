import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, F, ExpressionWrapper, fields
from django.utils import timezone
from datetime import timedelta
from core.models import EmailConfiguration, EmailCheck

logger = logging.getLogger('core')


@login_required(login_url='login/')
def index(request):
    """Dashboard index view"""
    # Get all configurations for the current user
    user_configs = EmailConfiguration.objects.filter(created_by=request.user)
    config_count = user_configs.count()
    active_config_count = user_configs.filter(is_active=True).count()

    # Get all checks for these configurations
    user_config_ids = user_configs.values_list('id', flat=True)
    checks = EmailCheck.objects.filter(configuration_id__in=user_config_ids)

    # Get counts by status
    status_counts = dict(checks.values_list('status').annotate(count=Count('status')))

    # Calculate success rate
    total_checks = checks.count()
    successful_checks = status_counts.get('received', 0)
    success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0

    # Get average delivery time for successful checks
    avg_delivery_time = checks.filter(
        status='received',
        delivery_time__isnull=False
    ).aggregate(avg_time=Avg('delivery_time'))['avg_time']

    # Get recent checks
    recent_checks = checks.order_by('-created_at')[:10]

    # Get checks from the last 24 hours
    last_24h = timezone.now() - timedelta(hours=24)
    checks_24h = checks.filter(created_at__gte=last_24h)
    checks_24h_count = checks_24h.count()

    # Calculate success rate for the last 24 hours
    successful_checks_24h = checks_24h.filter(status='received').count()
    success_rate_24h = (successful_checks_24h / checks_24h_count * 100) if checks_24h_count > 0 else 0

    context = {
        'config_count': config_count,
        'active_config_count': active_config_count,
        'total_checks': total_checks,
        'successful_checks': successful_checks,
        'failed_checks': status_counts.get('failed', 0),
        'pending_checks': status_counts.get('pending', 0) + status_counts.get('sent', 0),
        'success_rate': round(success_rate, 1),
        'avg_delivery_time': avg_delivery_time,
        'recent_checks': recent_checks,
        'checks_24h_count': checks_24h_count,
        'success_rate_24h': round(success_rate_24h, 1),
    }

    return render(request, 'dashboard/index.html', context)
