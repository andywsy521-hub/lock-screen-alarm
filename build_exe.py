import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'lock_screen_alarm.py',
    '--onefile',
    '--windowed',
    '--name=定时活动锁屏闹铃',
    '--icon=alarm_icon.ico'  # 可选，如果你有图标文件
])
