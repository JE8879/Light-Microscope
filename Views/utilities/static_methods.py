import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

class Utilities:

    @staticmethod
    def load_json_settings(parent=None):
        folder_path = 'Views/Utilities/settings/settings.json'

        with open(folder_path, 'r') as file:
            settings = json.load(file)
        return settings

    @staticmethod
    def show_message(parent=None, title=None, message=None):
        message_box = QMessageBox(parent)
        message_box.setWindowTitle(title)
        message_box.setText(message)
        message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        message_box.exec()
