
import os, sys


def up(n):
    path = os.path.abspath(__file__)
    return '/'.join(path.rstrip('/').split('/')[:-n])
repoPath = up(3)
sys.path = [repoPath] + sys.path + [repoPath]


#### PJ Settings:
PJ_PATH = [
    up(2) + '/colorflash/js',
    up(2) + '/mylib/js',
]
# Closure Compiler is slow to launch and run (> 1 sec),
# so you will rarely want have it on when developing
PJ_CLOJURE_MODE = None


#### Django settings:

DEBUG = True
ROOT_URLCONF = 'colorflash.urls'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
ADMINS = []
MIDDLEWARE_CLASSES = []
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)
TEMPLATE_DIRS = [up(1) + '/templates']







