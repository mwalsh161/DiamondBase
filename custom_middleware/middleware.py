from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile

from django.urls import reverse


def get_login_url():
    return reverse(settings.LOGIN_URL_NAME)


def get_exempts():
    exempts = [compile(get_login_url().lstrip('/'))]
    if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
        exempts += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]
    return exempts
