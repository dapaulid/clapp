#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import subprocess
import os


import command

import ansicolors
from ansicolors import colorize

STATUS_SUCCESS    = 0
STATUS_PENDING    = 1
STATUS_SKIPPED    = 2
STATUS_CANCELLED  = 3
STATUS_FAILED     = 4
STATUS_ERROR      = 5
STATUS_UNKNOWN    = -1

status_prettystr = {
    STATUS_SUCCESS    : colorize("√ OK", fg="green", style="bold"),
    STATUS_PENDING    : colorize("+", fg="gray"),
    STATUS_SKIPPED    : colorize("o skipped", fg="gray"),
    STATUS_CANCELLED  : colorize("% cancelled", fg="yellow"),
    STATUS_FAILED     : colorize("X FAILED", fg="red", style="bold"),
    STATUS_ERROR      : colorize("! ERROR", fg="white", bg="red", style="bold"),
    STATUS_UNKNOWN    : colorize("? unknown", fg="cyan"),
}

# to fix encoding error when redirecting to file (under Windows)
sys.stdout.reconfigure(encoding='utf-8')

def colorize_substr(frames, what, fg, bg, styles):
    return [x.replace(what, colorize(what, fg, bg, styles)) for x in frames]
        
class StatusIndicator:
    def __init__(self, text, multi_line = False):
        self.status = STATUS_UNKNOWN
        self.text = text
        self.multi_line = multi_line
        self.line = None
        self.count = 0
        self.value = None
        self.frames = colorize_substr(['●○○○', '○●○○', '○○●○', '○○○●', '○○●○', '○●○○'], '●', fg="yellow", bg=None, styles="bold")
        self.is_done = False
        self.format = '[ {0} ] {1}'
        self.start_time = time.time()
        self.elapsed_time_threshold = 0.100 # seconds
        
    def __enter__(self):
        self.update(STATUS_PENDING)
        return self
    def __exit__(self, exception_type, exception_value, traceback):
        if self.is_done:
            # nothing to do
            return
        # end if
        if exception_type is None:
            self.done(STATUS_UNKNOWN)
        elif exception_type is KeyboardInterrupt:
            self.done(STATUS_CANCELLED)
        else:
            self.done(STATUS_ERROR)
        # end if
    def update(self, status):
        if status == STATUS_PENDING and self.count > 0:
            if self.value != None:
                status_str = '%3d%%' % (self.value * 100)
            else:
                status_str = self.frames[self.count % len(self.frames)]
            # end if
        else:
            status_str = status_prettystr[status]
        # end if
        line = self.format.format(status_str, self.text)
        if not self.multi_line:
            if self.line != None:
                sys.stdout.write('\r')
                overpaint = ' ' * (len(self.line) - len(line)) # TODO does not work correctly with colors
            else:
                overpaint = ''
            # end if
            sys.stdout.write(line + overpaint)
            sys.stdout.flush()
        else:
            if self.count == 0:
                line += '...'
            # end if
            sys.stdout.write(line + '\n')
        # end if
        self.status = status
        self.line = line
        self.count += 1
    # end function

    def done(self, status, comments = []):
        if not self.is_done:
            if status != STATUS_SUCCESS and self.value != None:
                comments.append('at %d%%' % (self.value * 100))
            # end if
            elapsed = time.time() - self.start_time
            if self.elapsed_time_threshold != None and elapsed >= self.elapsed_time_threshold:
                comments.append('took %.3fs' % elapsed)
            # end if
            if comments:
                self.text += colorize(' (%s)' % (', '.join(comments)), fg="bright_black")
            # end if
            self.update(status)
            sys.stdout.write('\n')
            self.is_done = True
        # end if
    # end function

    def progress(self, value):
        self.value = value
        self.update(STATUS_PENDING)
    # end function

    def success(self):
        self.done(STATUS_SUCCESS)
    # end function

    def fail(self):
        self.done(STATUS_FAILED)
    # end function

    def skip(self, reason = None):
        self.done(STATUS_SKIPPED, ['reason: ' + reason] if reason != None else [])
    # end function

# end class

HRULE = '-' * 80

def exec(msg, cmd):
    # problems: 
    # - read non-blocking from process stdout to animate throbber
    # - let pipe appear as console for child process for proper flushing / progress parsing
    with StatusIndicator(msg, multi_line=True) as status:
        ansicolors.set_color('gray')
        print(HRULE)
        print('> ' + cmd)
        print(HRULE)
        exitcode = None
        try:
            exitcode = command.exec(cmd)
            print(HRULE)
            print('< process exited with code %s' % exitcode)
        finally:
            #subprocess.call('', shell=True) # workaround for non-working ANSI Escape Codes
            print(HRULE)
            ansicolors.reset_color()
        # end if
        if exitcode == 0:
            status.success()
        else:
            status.fail()
        # end
    # end with
# end function

""" with StatusIndicator("downloading internet") as status:
    for i in range(20):
        status.progress(i / 20)
        time.sleep(0.1)
    status.success()
    print("all stuff done") """

with StatusIndicator("removing old stuff") as status:
    if os.path.exists('test'):
        # TODO shutil.rmtree does not work for readonly files...
        subprocess.check_call('rmdir /s /q test', shell=True)
        status.success()
    else:
        status.skip("does not exist")
    # end if
# end with

exec("cloning git repository", 
    'git clone git@github.com:dapaulid/libremo.git test')
