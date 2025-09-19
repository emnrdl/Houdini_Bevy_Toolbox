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
from .ExportUtils import export_enabled_bevy_nodes, create_export_setup


def export_tab():
    # Create a new widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(QtCore.Qt.AlignTop)

    button2 = create_button("Export Bevy Enabled Nodes", export_enabled_bevy_nodes)
    main_layout.addWidget(button2)

    create_export_setup_button = create_button("Create Export Setup", create_export_setup)
    main_layout.addWidget(create_export_setup_button)

    main_widget.setLayout(main_layout)
    
    return main_widget
