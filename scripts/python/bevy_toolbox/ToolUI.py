from PySide6.QtWidgets import QPushButton

def create_button(text, callback):
    button = QPushButton(text)
    button.clicked.connect(callback)
    return button