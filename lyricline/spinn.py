import sys
import signal
import time
import threading

class Spinner:
    busy = False
    delay = 0.1
    message = ''
    thread = None

    def spinning_cursor(self):
        while 1: 
            for cursor in '◜◠◝◟◡◞':
                # handle SIGTERM
                yield '{} {}'.format(cursor, self.message)

    def __init__(self, delay=None, message=None):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.spinner_generator = self.spinning_cursor()

        if delay and float(delay):
            self.delay = delay

        if message and str(message):
            self.message = message

    def signal_handler(self, signal, frame):
        self.busy = False
        raise SystemExit
        sys.stdout.write('\x1b[2K')
        sys.stdout.write('\rExiting...\n')
        sys.stdout.flush()
        sys.exit(0)

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\r')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        self.thread = threading.Thread(target=self.spinner_task)
        self.thread.start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)

