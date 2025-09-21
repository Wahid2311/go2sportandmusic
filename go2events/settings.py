from pathlib import Path
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY =os.environ.get('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'anymail',
    'accounts',
    'events',
    'tickets'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'go2events.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
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

WSGI_APPLICATION = 'go2events.wsgi.application'

DATABASES = {
    'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
}


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



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATICFILES_DIRS=[BASE_DIR/'static']
STATIC_URL = 'static/'
STATIC_ROOT=os.path.join(BASE_DIR,'staticfiles')
STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

ANYMAIL = {
    "RESEND_API_KEY": os.environ.get('EMAIL_API_KEY'),
}
DEFAULT_FROM_EMAIL = os.environ.get('EMAIL_HOST_USER', '')

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/sign-in/'
SESSION_COOKIE_AGE = 36000 
SESSION_SAVE_EVERY_REQUEST = True

SUPERADMIN_EMAIL = os.environ.get('SUPERADMIN_EMAIL')
SUPERADMIN_PASSWORD = os.environ.get('SUPERADMIN_PASSWORD')

REVOLUT_API_KEY =os.environ.get('REVOLUT_API_KEY', '')
REVOLUT_PRODUCTION =True

BASE_URL =os.environ.get('BASE_URL', 'http://localhost:8000')
CSRF_TRUSTED_ORIGINS = [BASE_URL,'https://web-production-268f2.up.railway.app','https://go2sportandmusic.com']

AWS_ACCESS_KEY_ID =os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY =os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME =os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_FILE_OVERWRITE = False 
AWS_DEFAULT_ACL = 'private' 
USE_S3=True
AWS_S3_ADDRESSING_STYLE = 'virtual' 
AWS_S3_SIGNATURE_VERSION = 's3v4'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'
