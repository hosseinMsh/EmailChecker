import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EmailConfiguration, EmailCheck
from .forms import EmailConfigurationForm, RunCheckForm
from .tasks import send_test_email

logger = logging.getLogger('core')


@login_required
def configuration_list(request):
    """List all email configurations for the current user"""
    configurations = EmailConfiguration.objects.filter(created_by=request.user).order_by('-created_at')

    return render(request, 'core/configuration_list.html', {
        'configurations': configurations
    })


@login_required
def configuration_create(request):
    """Create a new email configuration"""
    if request.method == 'POST':
        form = EmailConfigurationForm(request.POST)
        if form.is_valid():
            configuration = form.save(commit=False)
            configuration.created_by = request.user
            configuration.save()

            messages.success(request, 'پیکربندی ایمیل با موفقیت ایجاد شد.')
            logger.info(f"User {request.user.username} created email configuration: {configuration.name}")

            return redirect('core:configuration_list')
    else:
        form = EmailConfigurationForm()

    return render(request, 'core/configuration_form.html', {
        'form': form,
        'title': 'ایجاد پیکربندی جدید'
    })


@login_required
def configuration_edit(request, pk):
    """Edit an existing email configuration"""
    configuration = get_object_or_404(EmailConfiguration, pk=pk, created_by=request.user)

    if request.method == 'POST':
        form = EmailConfigurationForm(request.POST, instance=configuration)
        if form.is_valid():
            form.save()

            messages.success(request, 'پیکربندی ایمیل با موفقیت بروزرسانی شد.')
            logger.info(f"User {request.user.username} updated email configuration: {configuration.name}")

            return redirect('core:configuration_list')
    else:
        form = EmailConfigurationForm(instance=configuration)

    return render(request, 'core/configuration_form.html', {
        'form': form,
        'configuration': configuration,
        'title': 'ویرایش پیکربندی'
    })


@login_required
def configuration_delete(request, pk):
    """Delete an email configuration"""
    configuration = get_object_or_404(EmailConfiguration, pk=pk, created_by=request.user)

    if request.method == 'POST':
        name = configuration.name
        configuration.delete()

        messages.success(request, f'پیکربندی "{name}" با موفقیت حذف شد.')
        logger.info(f"User {request.user.username} deleted email configuration: {name}")

        return redirect('core:configuration_list')

    return render(request, 'core/configuration_confirm_delete.html', {
        'configuration': configuration
    })


@login_required
def check_list(request):
    """List all email checks for the current user's configurations"""
    # Get all configurations for the current user
    user_configs = EmailConfiguration.objects.filter(created_by=request.user).values_list('id', flat=True)

    # Get all checks for these configurations
    checks = EmailCheck.objects.filter(configuration_id__in=user_configs)

    # Apply filters if provided
    status_filter = request.GET.get('status')
    if status_filter:
        checks = checks.filter(status=status_filter)

    search_query = request.GET.get('q')
    if search_query:
        checks = checks.filter(
            Q(message_id__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(error_message__icontains=search_query)
        )

    # Order by created_at (newest first)
    checks = checks.order_by('-created_at')

    # Paginate the results
    paginator = Paginator(checks, 20)  # 20 checks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/check_list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query
    })


@login_required
def check_detail(request, pk):
    """View details of a specific email check"""
    # Get all configurations for the current user
    user_configs = EmailConfiguration.objects.filter(created_by=request.user).values_list('id', flat=True)

    # Get the check if it belongs to one of the user's configurations
    check = get_object_or_404(EmailCheck, pk=pk, configuration_id__in=user_configs)

    return render(request, 'core/check_detail.html', {
        'check': check
    })


@login_required
def run_check(request):
    """Run an immediate email check"""
    if request.method == 'POST':
        form = RunCheckForm(request.POST)

        # Only show configurations belonging to the current user
        form.fields['configuration'].queryset = EmailConfiguration.objects.filter(
            created_by=request.user,
            is_active=True
        )

        if form.is_valid():
            configuration = form.cleaned_data['configuration']

            # Start the email check task
            send_test_email.delay(configuration.id)

            messages.success(
                request,
                f'بررسی ایمیل برای پیکربندی "{configuration.name}" آغاز شد. نتایج به زودی قابل مشاهده خواهند بود.'
            )
            logger.info(f"User {request.user.username} started manual email check for: {configuration.name}")

            return redirect('core:check_list')
    else:
        form = RunCheckForm()

        # Only show configurations belonging to the current user
        form.fields['configuration'].queryset = EmailConfiguration.objects.filter(
            created_by=request.user,
            is_active=True
        )

    return render(request, 'core/run_check.html', {
        'form': form
    })
