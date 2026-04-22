import os
import sys
import threading
import time

from django.apps import AppConfig


def _poll_loop():
    while True:
        time.sleep(60)
        try:
            from .views import check_generating_songs
            check_generating_songs()
        except Exception:
            pass


class MyappConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        # Dev server spawns reloader + child (RUN_MAIN=true on child).
        # Skip reloader to avoid two threads.
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
        thread = threading.Thread(target=_poll_loop, daemon=True, name='suno-poller')
        thread.start()
