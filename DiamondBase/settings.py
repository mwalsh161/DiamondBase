"""
Django settings for DiamondBase project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, json, re

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(THIS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Load .env (should be kept secret from repo and server)
# Load environment variables directly to namespace
with open(os.path.join(THIS_DIR,'.env'),'r') as fid:
    # Replace any python escaped code in .env
    contents = fid.read()
    to_replace = [(m.groups()[0],m.start(),m.end()) for m in re.finditer(r'{{(.*?)}}',contents)]
    to_replace.reverse()
    for [val,start,end] in to_replace:
        evaled = eval(val)
        evaled = json.dumps(evaled)[1:-1] # Remove quotes
        contents = contents[0:start] + evaled + contents[end:]
    locals().update(json.loads(contents))


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sample_database',
    'ip_tracker',
    'foundation',
    'slack',
    'about',
    'login_required'
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'login_required.middleware.LoginRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                 "django.contrib.auth.context_processors.auth",
                 "django.template.context_processors.debug",
                 "django.template.context_processors.i18n",
                 "django.template.context_processors.media",
                 "django.template.context_processors.static",
                 "django.template.context_processors.tz",
                 "django.contrib.messages.context_processors.messages",
                 "django.template.context_processors.request",
                 "sample_database.context_processors.action_types",
                 "sample_database.context_processors.lab_name"
            ],
        },
    },
]

ROOT_URLCONF = 'DiamondBase.urls'

WSGI_APPLICATION = 'DiamondBase.wsgi.application'

LOGIN_URL = '/login/'

LOGIN_URL_NAME = 'login'

LOGIN_EXEMPT_URLS = (
    r'^slack/',
)

LOGIN_REDIRECT_URL = '/'

LOGOUT_REDIRECT_URL = '/'

LOGIN_REQUIRED_IGNORE_VIEW_NAMES = [
    'login',
    'logout'
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES defined in .env

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

#TIME_ZONE defined in .env

USE_TZ = True

USE_I18N = False

#USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

MEDIA_URL = '/media/'
# MEDIA_ROOT defined in .env
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT_PATH, 'static/')
#STATICFILES_DIRS = (os.path.join(PROJECT_ROOT_PATH, 'static/'),)
