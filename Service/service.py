from aiohttp import web
import asyncio
import config
from main import app
from pystray import Icon, Menu, MenuItem
from PIL import Image
from pywinauto import Application
import subprocess
import sys
from threading import Thread, Event
import time
import win32.lib.win32con as win32con
from win32 import win32gui

app_kill_flag = Event()
app_thread: Thread
state = False

ui_subprocess: subprocess.Popen = None
ui_app: Application = None
ui_app_thread: Thread

def nop():
    pass

def show_systray():
    image = Image.open('./icon.png')
    icon = Icon('BTread', image, 'BTread')

    def show_application():
        global ui_app, open_ui_app
        if ui_app:
            win32gui.ShowWindow(ui_app.top_window().handle, win32con.SW_NORMAL)
            win32gui.SetForegroundWindow(ui_app.top_window().handle)
        else:
            open_ui_app()

    def on_exit():
        global app_kill_flag, app_thread, nop, ui_app_thread
        nonlocal icon
        icon.stop()
        app_kill_flag.set()
        app_thread.join()
        ui_app_thread.join()

    icon.menu = Menu(
        MenuItem(
            'BTread',
            nop,
            enabled=False,
        ),
        Menu.SEPARATOR,
        MenuItem(
            'Show Application',
            show_application,
            default=True
        ),
        Menu.SEPARATOR,
        MenuItem(
            'Exit',
            on_exit,
        )
    )

    icon.run()

def _handle_task_result(task: asyncio.Task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(e)

def start_server():
    web.run_app(app, host='localhost', port=8826)

async def app_kill_watcher_init(this_app):
    app_kill_watcher_task = asyncio.create_task(app_kill_watcher())
    app_kill_watcher_task.add_done_callback(_handle_task_result)

async def app_kill_watcher():
    global app, app_kill_flag
    while not app_kill_flag.is_set():
        await asyncio.sleep(3)
    print("Start shutting down")
    await app.shutdown()
    print("Start cleaning up")
    await app.cleanup()
    sys.exit(0)

def ui_app_watcher():
    global ui_app, ui_subprocess, app_kill_flag
    while not app_kill_flag.is_set():
        if ui_subprocess is None:
            ui_app = None
        else:
            return_code = ui_subprocess.poll()
            if return_code is not None:
                ui_subprocess = None
                ui_app = None
        time.sleep(3)
    if ui_subprocess is not None:
        ui_subprocess.kill()

def open_ui_app():
    global ui_app, ui_subprocess
    ui_subprocess = subprocess.Popen(config.UI_EXE_PATH)
    ui_app = Application().connect(process=ui_subprocess.pid)

if __name__ == '__main__':
    app.on_startup.append(app_kill_watcher_init)
    app_thread = Thread(target=start_server)
    app_thread.start()
    open_ui_app()
    ui_app_thread = Thread(target=ui_app_watcher)
    ui_app_thread.start()
    show_systray()