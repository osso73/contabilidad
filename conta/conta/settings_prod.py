from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['192.168.1.28', 'conta.opr.duckdns.org']

with open('/usr/local/etc/conta/secret_key') as f:
    SECRET_KEY = f.read().strip()
