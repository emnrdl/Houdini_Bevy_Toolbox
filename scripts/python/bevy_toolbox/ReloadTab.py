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

from .ToolUI import create_button
from .ReloadUtils import reload_all_fbx_nodes

def reload_tab():
    # Create a new widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(QtCore.Qt.AlignTop)

    # add buttons
    button1 = create_button("Reload All FBX Nodes", reload_all_fbx_nodes)
    main_layout.addWidget(button1)

    main_widget.setLayout(main_layout)

    return main_widget
