import hou
import os
import subprocess
import time
import win32gui
from PySide6 import QtWidgets, QtCore, QtGui
from .ToolUI import create_button

def run_bevy_viewer():

    pass



class BevyViewerPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.process = None
        self.embedded_window = None
        self.container = None

        self.start_btn = QtWidgets.QPushButton("Start")
        self.stop_btn = QtWidgets.QPushButton("Stop")

        self.viewer_host = QtWidgets.QWidget()
        self.viewer_host.setMinimumSize(640, 360)
        self.viewer_host_layout = QtWidgets.QVBoxLayout(self.viewer_host)
        self.viewer_host_layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QtWidgets.QHBoxLayout()
        top_bar.addWidget(self.start_btn)
        top_bar.addWidget(self.stop_btn)
        top_bar.addStretch()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top_bar)
        layout.addWidget(self.viewer_host)

        self.start_btn.clicked.connect(self.start_bevy)
        self.stop_btn.clicked.connect(self.stop_bevy)

    def start_bevy(self):
        if self.process is not None:
            return

        # get all bevyconfig node
        bevyconfig_nodes = hou.node("/obj").children()
        bevyconfig_nodes = [node for node in bevyconfig_nodes if hou.hda.componentsFromFullNodeTypeName(node.type().name())[2] == "Bevy_Config"]
        
        if len(bevyconfig_nodes) == 0:
            #show error message
            hou.ui.displayMessage("No BevyConfig nodes found")
            return
        if len(bevyconfig_nodes) > 1:
            hou.ui.displayMessage("Multiple BevyConfig nodes found")
            return
        else:

            bevy_exe = r"C:\path\to\your\bevy_viewer.exe"

            self.process = QtCore.QProcess(self)
            self.process.start(bevy_exe)

            if not self.process.waitForStarted(3000):
                print("Bevy process failed to start")
                self.process = None
                return

            QtCore.QTimer.singleShot(1500, self.try_embed_bevy_window)

    def stop_bevy(self):
        if self.container is not None:
            self.container.setParent(None)
            self.container.deleteLater()
            self.container = None

        self.embedded_window = None

        if self.process is not None:
            self.process.kill()
            self.process.waitForFinished(2000)
            self.process = None

    def try_embed_bevy_window(self):
        hwnd = self.find_bevy_window_handle_windows()
        if not hwnd:
            print("Bevy window handle not found")
            return

        self.embedded_window = QtGui.QWindow.fromWinId(hwnd)
        self.container = QtWidgets.QWidget.createWindowContainer(
            self.embedded_window,
            self.viewer_host
        )
        self.viewer_host_layout.addWidget(self.container)

    def find_bevy_window_handle_windows(self):
        # Windows için pywin32 ile bulabilirsin.
        # Başlık adına göre pencere ara.
        try:
            import win32gui

            target_title = "Bevy Viewer"

            result = []

            def enum_handler(hwnd, _):
                title = win32gui.GetWindowText(hwnd)
                if target_title in title and win32gui.IsWindowVisible(hwnd):
                    result.append(hwnd)

            win32gui.EnumWindows(enum_handler, None)
            return result[0] if result else None
        except Exception as e:
            print("Window search error:", e)
            return None

import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [
    ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM),
    wintypes.LPARAM,
]
EnumWindows.restype = wintypes.BOOL

GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [wintypes.HWND]
GetWindowTextLengthW.restype = ctypes.c_int

GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
GetWindowTextW.restype = ctypes.c_int

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL

def find_window_by_title_contains(title_substring: str):
    matches = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, lParam):
        if not IsWindowVisible(hwnd):
            return True

        length = GetWindowTextLengthW(hwnd)
        if length == 0:
            return True

        buffer = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buffer, length + 1)
        title = buffer.value

        if title_substring.lower() in title.lower():
            matches.append(hwnd)

        return True

    EnumWindows(enum_proc, 0)
    return matches[0] if matches else None