import hou
import os
from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QStackedLayout,
    QPushButton,
    QTabWidget,
)
from PySide6 import QtCore

from .BevySceneView import bevySceneView

def create_viewer_layout():
    # Create a new widget
    main_widget = QWidget()
    main_layout = bevySceneView()

    main_widget.setLayout(main_layout)

    return main_widget