from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))  # أو أي عنوان URL لصفحة تسجيل الدخول
        elif request.user.is_admin == 0:
             return redirect(reverse('login'))  # أو أي عنوان URL لصفحة الخطأ
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view

def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))  # أو أي عنوان URL لصفحة تسجيل الدخول
        elif request.user.is_employee == 0:
             return redirect(reverse('login'))  # أو أي عنوان URL لصفحة الخطأ
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view

def citizen_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))  # أو أي عنوان URL لصفحة تسجيل الدخول
        elif request.user.is_employee  or request.user.is_admin  :
             return redirect(reverse('login'))  # أو أي عنوان URL لصفحة الخطأ
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view


def employee_and_admin(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))  # أو أي عنوان URL لصفحة تسجيل الدخول
        elif request.user.is_employee == 0  and request.user.is_admin == 0  :
             return redirect(reverse('login'))  # أو أي عنوان URL لصفحة الخطأ
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view
