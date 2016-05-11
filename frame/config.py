# -*- coding:utf-8 -*-
__author__ = 'Ulric Qin'

# -- app config --
DEBUG = True

# -- portal db config --
PORTAL_DB_HOST = "127.0.0.1"
PORTAL_DB_PORT = 3306
PORTAL_DB_USER = "root"
PORTAL_DB_PASS = ""
PORTAL_DB_NAME = "falcon_portal"

# -- uic db config
UIC_DB_HOST = "127.0.0.1"
UIC_DB_PORT = 3306
UIC_DB_USER = "root"
UIC_DB_PASS = ""
UIC_DB_NAME = "uic"

# -- cookie config --
SECRET_KEY = "4e.5tyg8-u9ioj"
SESSION_COOKIE_NAME = "falcon-portal"
PERMANENT_SESSION_LIFETIME = 3600 * 24 * 30

UIC_ADDRESS = {
    'internal': 'http://127.0.0.1:8080',
    'external': 'http://11.11.11.11:8080',
}

UIC_TOKEN = ''

MAINTAINERS = ['root']
CONTACT = 'ulric.qin@gmail.com'

COMMUNITY = True

try:
    from frame.local_config import *
except Exception, e:
    print "[warning] %s" % e
