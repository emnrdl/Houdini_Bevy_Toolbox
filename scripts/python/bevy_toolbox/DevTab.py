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
from .DevUtils import print_node_type, cargo_run, show_create_bevy_project, open_project_in_vs_code


def Development_tab():
    # Create a new widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()
    main_layout.setAlignment(QtCore.Qt.AlignTop)



    # add buttons
    create_project_button = create_button("Create Bevy Project", show_create_bevy_project)
    main_layout.addWidget(create_project_button)

    cargo_run_button = create_button("Cargo Run", cargo_run)
    main_layout.addWidget(cargo_run_button)

    open_vscode_button = create_button("Open in VS Code", open_project_in_vs_code)
    main_layout.addWidget(open_vscode_button)

    print_node_name = create_button("Print Node Name", print_node_type)
    main_layout.addWidget(print_node_name)

    main_widget.setLayout(main_layout)

    return main_widget
