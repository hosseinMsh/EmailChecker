from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from account.forms import LoginForm, RegisterForm
import logging
logger = logging.getLogger(__name__)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'خوش آمدید، {user.username}!')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است.')
    else:
        form = LoginForm()

    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'شما با موفقیت خارج شدید.')
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید.')
            return redirect('login')
        else:
            messages.error(request, 'لطفاً خطاهای فرم را اصلاح کنید.')
    else:
        form = RegisterForm()

    return render(request, 'account/register.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    username = request.user.username
    logout(request)
    logger.info(f"User {username} logged out")
    return redirect('login')
