#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2023 ahrbe1
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import datetime
import tkinter as tk
import json
import os
from threading import Timer, Lock

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

CONFIG_FILE_PATH = os.path.expanduser('~/.chatgpt-quota.conf')

KEY_WINDOW_STATE = 'window-state'
KEY_TIMESTAMPS = 'message-times'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return hours, minutes, seconds

class GptQuotaTracker:
    def __init__(self):
        self.quota_messages = 25
        self.quota_duration_sec = 3 * 60 * 60 # 3 hours
        self.message_times = [ ]
        self.font = ('Consolas', 18)
        self.lock = Lock()
        self.window = None
        self.label = None
        self.button = None
        self.timer = None

        # message limits with corresponding colors
        self.colors = [
            (15, '#00ff00'), # bright green
            (6, '#f2e200'),  # bright yellow
            (1, '#ff0000'),  # red
            (0, 'grey')
        ]

    def on_timer_expired(self):
        self.periodic_cleanup()
        self.on_refresh()
        self.timer = Timer(1, self.on_timer_expired)
        self.timer.start()

    def on_refresh(self):
        with self.lock:
            count = self.quota_messages - len(self.message_times)
            color = 'white'
            for p in self.colors:
                if count >= p[0]:
                    color = p[1]
                    break
            next_in = 'N/A'
            if len(self.message_times) > 0:
                duration = datetime.timedelta(seconds=self.quota_duration_sec) - \
                    (datetime.datetime.now() - self.message_times[0])
                hrs, mins, sec = convert_timedelta(duration)
                next_in = '{}h {}m {}s'.format(hrs, mins, sec)
            self.label['text'] = 'Remaining: ' + str(count) + '\nNext in: ' + next_in
            self.label['fg'] = color
            if count == 0:
                self.button['state'] = 'disabled'
            else:
                self.button['state'] = 'normal'

    def periodic_cleanup(self):
        with self.lock:
            self.message_times = [
                x for x in self.message_times
                    if x >= datetime.datetime.now() + \
                        datetime.timedelta(seconds=-self.quota_duration_sec) ]
        self.on_refresh()

    def on_click(self):
        self.message_times.append(datetime.datetime.now())
        self.on_refresh()

    def save_state(self):
        state = {
            KEY_WINDOW_STATE: self.window.geometry(),
            KEY_TIMESTAMPS: [ x.strftime(DATETIME_FORMAT) for x in self.message_times ]
        }

        with open(CONFIG_FILE_PATH, 'w+') as f:
            f.write(json.dumps(state, indent=2))

    def load_state(self):
        try:
            state = None
            with open(CONFIG_FILE_PATH, 'r') as f:
                state = json.loads(f.read())

            state[KEY_TIMESTAMPS] = \
                [datetime.datetime.strptime(x, DATETIME_FORMAT) for x in state[KEY_TIMESTAMPS]]
        except:
            pass
        return state

    def on_close(self):
        self.timer.cancel()
        self.timer = None
        self.save_state()
        self.window.quit()
        self.window.destroy()

    def main(self):
        self.window = tk.Tk()
        state = self.load_state()

        if state:
            self.window.geometry(state[KEY_WINDOW_STATE])
            self.message_times = state[KEY_TIMESTAMPS]
        else:
            self.window.geometry("500x300")

        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.title('ChatGPT Quota Tracker')

        # enable always on-top mode
        self.window.attributes('-topmost', True)

        self.label = tk.Label(self.window, text="Remaining: ",
            font=self.font, bg='#424751', fg=self.colors[0][1])
        self.label.pack(side="top", fill="both", expand=True)

        self.button = tk.Button(self.window, text="Add Message",
            command=self.on_click, font=self.font, bg='#33353f', fg='white')
        self.button.pack(side="bottom", fill="both", expand=True)

        self.on_refresh()
        self.timer = Timer(1, self.on_timer_expired)
        self.timer.start()
        self.window.mainloop()

if __name__ == '__main__':
    sys.exit(GptQuotaTracker().main())

