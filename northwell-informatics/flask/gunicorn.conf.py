# Gunicorn configuration file for Flask SOP Query Application
# ==========================================================

import multiprocessing
import os
from pathlib import Path

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'flask_sop_query'

# Server mechanics
daemon = False  # Set to True for background daemon mode
pidfile = '/tmp/gunicorn_flask_sop.pid'
user = None
group = None
tmp_upload_dir = None

# SSL/HTTPS Configuration (disabled for HTTP mode)
# keyfile = None
# certfile = None  
# ssl_version = None
# cert_reqs = None
# ca_certs = None
# suppress_ragged_eofs = True

# Application
# The WSGI application
wsgi_module = "app:app"

# Environment variables
raw_env = [
    'PYTHONPATH=../yjacobs/modules:../yjacobs'
]

# Preload application for better performance
preload_app = True

# Enable threading
threads = 2

# Maximum number of pending connections
listen = 128
