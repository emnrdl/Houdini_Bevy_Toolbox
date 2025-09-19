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
from .FileUtils import open_file_location


def file_tab():
    # Create a new widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(QtCore.Qt.AlignTop)

    # add buttons
    button1 = create_button("Open File Location", open_file_location)
    main_layout.addWidget(button1)

    main_widget.setLayout(main_layout)

    return main_widget

def create_bevy_directory_node():
    # Create a new directory node in the Bevy output folder
    output_dir = os.path.join(hou.session.path(), "bevy_output")
    bevy_node = hou.node("/obj").createNode("geo", "bevy_output")
    bevy_node.setPosition(hou.Vector2(0, 0))
    return bevy_node