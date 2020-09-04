"""
Django settings for core project.
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'turm6@ov0v%k*02@lr+$b!bhn79sy14z_77%6)eg5-zt#xs2=^'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'docker.sqlite3'),
    }
}


DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'keys.apps.KeysConfig',
    'stats.apps.StatsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    'django_extensions',
    'octicons',
    'freeze',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'app.urls'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'app', 'templates'),
            os.path.join(BASE_DIR, 'keys', 'templates'),
            os.path.join(BASE_DIR, 'stats', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'nl-NL'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = False
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
STATIC_URL = '/static/'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

#LOGIN_REDIRECT_URL = '/medslist'
#LOGOUT_REDIRECT_URL = '/medslist'

SOUTH_TESTS_MIGRATE = False

#the absolute path where to store the .zip and the html files
#default value is a folder named 'freeze' located as sibling of 'settings.MEDIA_ROOT'
FREEZE_ROOT = '/var/tmp/freeze'

#tells 'freeze' if the urls should be fetched using https instead of http protocol (only if FREEZE_SITE_URL is not defined)
FREEZE_USE_HTTPS = False

#the site-url to crawl, if not specified it will be autodetected using the sites app
FREEZE_SITE_URL = 'http://localhost:8000'

#the base-url for all links relative to root '/'
#useful if the generated static site will run in a specific folder which is not the document-root
FREEZE_BASE_URL = None

#if True 'freeze' will convert all absolute urls to relative urls
#useful if the generated static site will run locally (file://) or in an unknown folder which is not the document-root (only if FREEZE_BASE_URL is not defined)
#FREEZE_RELATIVE_URLS = False
FREEZE_RELATIVE_URLS = False

#if True 'freeze' will inject a script at the end of each page
#which will force hrefs like 'path/' to 'path/index.html' (only if the site is running under file://)
#useful if the generated static site will run locally (requires FREEZE_RELATIVE_URLS set to True) to prevent local directory index
#FREEZE_LOCAL_URLS = False
FREEZE_LOCAL_URLS = False

#if True 'freeze' will fetch each url founded in sitemap.xml
FREEZE_FOLLOW_SITEMAP_URLS = True

#if True 'freeze' will follow and fetch recursively each link-url founded in each page
FREEZE_FOLLOW_HTML_URLS = True

#if true 'freeze' will send an email to managers containing the list of all invalid urls (404, 500, etc..)
FREEZE_REPORT_INVALID_URLS = False

#the invalid urls email report subject
FREEZE_REPORT_INVALID_URLS_SUBJECT = '[freeze] invalid urls'

#if True the generated site will contain also the MEDIA folder and ALL its content
FREEZE_INCLUDE_MEDIA = True
#elif the value is a list or tuple only the specified directories will be included
FREEZE_INCLUDE_MEDIA = ('cache', 'images', 'videos', )

#if True the generated site will contain also the STATIC folder and ALL its content
FREEZE_INCLUDE_STATIC = True
#elif the value is a list or tuple only the specified directories will be included
FREEZE_INCLUDE_STATIC = ('keys', 'stats')

#if True the generated site will be zipped, the *.zip file will be created in FREEZE_ROOT
FREEZE_ZIP_ALL = False

#the name of the zip file created
FREEZE_ZIP_NAME = 'freeze'

#The request headers to use during the get requests that scrape the site
#can be used to set Authentication headers, by default sets the user-agent
FREEZE_REQUEST_HEADERS = {'user-agent': 'django-freeze'}

# django-directory
INSTALLED_APPS += ['directory']
DIRECTORY_DIRECTORY = 'datastore'
DIRECTORY_TEMPLATE = 'directory/list.html'

KEYSETS_PAGINATE_BY = 20

# Activate Django-Heroku.
django_heroku.settings(locals())
