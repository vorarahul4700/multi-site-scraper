import os

# Railway injects PORT at runtime — read it directly in Python, no shell needed
bind = "0.0.0.0:{}".format(os.environ.get("PORT", "5050"))
workers = 2
threads = 4
timeout = 120
worker_class = "sync"
