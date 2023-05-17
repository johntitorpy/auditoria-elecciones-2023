from __future__ import absolute_import
from logging import INFO as logging_INFO

# settings relativas a logging
DEFAULT_LOG_LEVEL = logging_INFO
LOGGING_SERVER_HOST = 'localhost'

# settings para logging local
LOG_TO_FILE = False
LOG_TO_DB = False
LOG_TO_STDOUT = False
LOG_TO_SENTRY = False
LOG_TO_LOGSTASH = False
LOG_SENTRY_PATH = ''

LOG_CAPTURE_STDOUT = False

FILELOG_SIZE = 100000
FILELOG_ROTATION = 9
LOG_NAME = "/var/log/msa/%s.log"

# Settings logstash
LOGSTASH_HOST_DOCKER = "logstash"

LOGSTASH_HOST = LOGSTASH_HOST_DOCKER
LOGSTASH_PORT = 5044
LOGSTASH_ENVIRONMENT = "development"
LOGSTASH_LOG_LEVEL = logging_INFO
LOGSTASH_TRANSPORT = "logstash_async.transport.BeatsTransport"
LOGSTASH_ASYNC = True
LOGSTASH_DB_PATH = "/tmp/%s_logstash.db"

try:
    from msa.core.logging.settings_local import *
except ImportError:
    pass
