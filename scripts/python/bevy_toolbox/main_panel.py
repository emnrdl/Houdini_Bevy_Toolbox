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

from .ExportTab import export_tab
from .DevTab import Development_tab
from .FileTab import file_tab
from .ReloadTab import reload_tab

def create_toolbox():
    # Create a new widget
    main_widget = QWidget()
    main_layout = QVBoxLayout()

    tab_widget = QTabWidget()

    from .ExportTab import export_tab
    from .DevTab import Development_tab
    from .FileTab import file_tab
    from .ReloadTab import reload_tab

    tab_widget.addTab(Development_tab(), "Development")
    tab_widget.addTab(export_tab(), "Export")
    tab_widget.addTab(file_tab(), "File")
    tab_widget.addTab(reload_tab(), "Reload")

    main_layout.addWidget(tab_widget)
    main_widget.setLayout(main_layout)

    return main_widget