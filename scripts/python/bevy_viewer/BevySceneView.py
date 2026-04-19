import hou
import os
from PySide6.QtWidgets import(
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QPushButton,
    QTabWidget,
    QLabel,
    QGraphicsPixmapItem,
)
from PySide6.QtGui import QPixmap
from PySide6 import QtCore
from .ToolUI import create_button
from .BevySceneViewUtils import run_bevy_viewer, BevyViewerPanel

def bevySceneView():
    # Create a new widget
    main_layout = QVBoxLayout()
    main_layout.setAlignment(QtCore.Qt.AlignTop)

    main_layout.addWidget(BevyViewerPanel())


    # hor_layout = QHBoxLayout()
    # hor_layout.setAlignment(QtCore.Qt.AlignCenter)
    # main_layout.addLayout(hor_layout)
    


    # add buttons
    # run_button = create_button("Run", run_bevy_viewer)
    # hor_layout.addWidget(run_button)
    

    # stop_button = create_button("Stop", lambda: print("Stop button clicked"))
    # hor_layout.addWidget(stop_button)

    return main_layout


