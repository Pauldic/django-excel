"""
Django settings for mysite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
import django
from core.decouple import config, Csv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '&kzg)(b_xt1*nyp-s97ibt01b7p+67#&-brmb_nqj&dn_%q6tc'
SECRET_KEY = config('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = config('DEBUG', default=True, cast=bool)
LOGGING_LEVEL = config('LOGGING_LEVEL', default='INFO')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*', cast=Csv())

PROJECT_NAME = 'mysite'
TEMPLATE_THEME = 'default'

SITE_ID = 1
ADMINS = (('Administrator', 'support@gmbenefit.org'), ('Tester', 'donationmove@gmail.com'),)
MANAGERS = ADMINS


# APPEND_SLASH = True
# ADMIN_URL = 'access/'
# LOGIN_URL = 'account:login'
# LOGOUT_URL = 'account:logout'
# LOGIN_REDIRECT_URL = 'core:dashboard'
# LOGOUT_REDIRECT_URL = 'core:index'
# Application definition

FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                        "django_excel.TemporaryExcelFileUploadHandler")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    
    'core.apps.CoreConfig',
    'import_export'
]

if DEBUG:
    INSTALLED_APPS.append("sslserver")


COMMON_MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
)

if django.VERSION[0] > 1:
    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        *COMMON_MIDDLEWARE
    )

else:
    MIDDLEWARE_CLASSES = COMMON_MIDDLEWARE


ROOT_URLCONF = 'mysite.urls'

WSGI_APPLICATION = 'mysite.wsgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    },
]


IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_LOG = False
IMPORT_EXPORT_TMP_STORAGE_CLASS = 'import_export.tmp_storages.TempFolderStorage'
IMPORT_EXPORT_IMPORT_PERMISSION_CODE = None
IMPORT_EXPORT_EXPORT_PERMISSION_CODE = None
IMPORT_EXPORT_CHUNK_SIZE = 100


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [os.path.join(BASE_DIR, PROJECT_NAME + "/" + TEMPLATE_THEME)]

DEEP_STATIC_COLLECT = config('DEEP_STATIC_COLLECT', default=True, cast=bool)
if DEEP_STATIC_COLLECT:
    STATICFILES_DIRS.append(os.path.join(BASE_DIR, PROJECT_NAME + "/assets"))
    
    
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'formatters': {
        'verbose': {
            # ERROR|25/Apr/2017 17:30:22|basehttp|25069|139803081283328|"POST /system/secured/admin/core/package/add/ HTTP/1.1" 500 59
            'format': '%(levelname)s|%(asctime)s|%(module)s|%(process)d|%(thread)d|%(message)s',
            'datefmt': "%Y-%d-%b %H:%M:%S"
        },
        'standard': {
            # [ERROR]25-Apr-2017 17:52:24|django.server|"POST /system/secured/admin/core/package/add/ HTTP/1.1" 500 59
            'format': '[%(levelname)s]%(asctime)s|%(name)s|%(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {'format': '%(levelname)s|%(asctime)s|%(message)s', 'datefmt': "%Y-%m-%d %H:%M:%S"},
        'too-simple': {'format': '%(message)s'},
    },

    'handlers': {
        'null': {
            'level': LOGGING_LEVEL,
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': LOGGING_LEVEL,
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
            'email_backend': 'django.core.mail.backends.smtp.EmailBackend',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'too-simple',
            'stream': sys.stdout,
        },
        'log_file': {
            'level': LOGGING_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, PROJECT_NAME + '.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'standard',
        },
    },

    'loggers': {
        PROJECT_NAME + '.tasks': {
            'handlers': ['mail_admins'],
            'propagate': True,
        },
        # PROJECT_NAME: {
        #     'handlers': ['mail_admins', 'console', 'log_file'],
        #     'propagate': True,
        # },
        # 'core.*.*': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
        # 'core.overrides': {
        #     'handlers': ['console'],
        #     'propagate': True,
        # },
        # 'core.*': {
        #     'handlers': ['mail_admins', 'console', 'log_file'],
        #     'propagate': True,
        # },
        PROJECT_NAME+'.*': {
            'handlers': ['mail_admins', 'console', 'log_file'],
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['log_file'],
            'propagate': True,
        },
        'django.security.*': {
            'handlers': ['mail_admins', 'log_file'],
            'propagate': True,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django_redis.cache': {
            'handlers': ['log_file', 'console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'log_file'],
            'propagate': True,
        },
        'django': {
            'handlers': ['log_file', 'console'],
            'propagate': True,
        },
        'root': {
            'handlers': ['console'],
        }
    },
}

# USE_THOUSAND_SEPARATOR = True
# THOUSAND_SEPARATOR = ','
