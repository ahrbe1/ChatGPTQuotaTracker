# ChatGPTQuotaTracker
A simple Python application to track ChatGPT Quota

This small app will help you manually track your ChatGPT quota.

The current quota is 25 messages / 3 hours. 

Requirements: Python 3 with tkinter

Features:
- Shows messages remaining and time to next message
- Color coded text shows when you hit various pre-defined message limits:
  - Green: 15-25 messages remaining
  - Yellow: 6-14
  - Red: 1-5
  - Black: 0
- Persistent state (window position, size, and message timestamps)

Config file is located at: `~/.chatgpt-quota.conf`

License: MIT
