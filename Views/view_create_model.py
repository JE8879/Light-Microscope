import os
import sys
from watchdog.observers import Observer
from PyQt6 import uic
from PyQt6.QtGui import QFileSystemModel, QGuiApplication
from PyQt6.QtWidgets import QPushButton, QApplication, QLabel, QSpinBox, QLineEdit, QRadioButton, QWidget, QTreeView, QProgressBar

from . utilities.video_processing import VideoProcessing
from . utilities.static_methods import Utilities
from . utilities.change_handler import ChangeHandler

class ViewCreateModel(QWidget):
    # Constructor
    def __init__(self):
        super(ViewCreateModel, self).__init__()

        # Properties
        self.image_processing_instance = None

        # Load settings
        json_settings = Utilities.load_json_settings()
        self.models_path = json_settings['directories']['models']

        # Call draw components
        self.draw_components()
        self.manage_signals()
        self.load_directories()
        self.set_center_window()

    def draw_components(self):
        # Load template
        uic.loadUi('Templates/viewCreateModel.ui', self)

        self.text_model = self.findChild(QLineEdit, 'text_model')

        self.rdb_by_time = self.findChild(QRadioButton, 'rdb_by_time')
        self.rdb_by_quantity = self.findChild(QRadioButton, 'rdb_by_quantity')

        self.folders_tree = self.findChild(QTreeView, 'folders_tree')

        self.spin_by_time = self.findChild(QSpinBox, 'spin_by_time')
        self.spin_by_quantity = self.findChild(QSpinBox, 'spin_by_quantity')

        self.creation_progress = self.findChild(QProgressBar, 'creation_progress')
        
        self.btn_create_model = self.findChild(QPushButton, 'btn_create_model')
        self.btn_start = self.findChild(QPushButton, 'btn_start')
        self.btn_cancel = self.findChild(QPushButton, 'btn_cancel')

        self.lbl_image_result = self.findChild(QLabel, 'lbl_image_result')
        # self.lbl_info_directory = self.findChild(QLabel, 'lbl_info_directory')
    
    def set_center_window(self):
        qr = self.geometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        if(isinstance(self.image_processing_instance, VideoProcessing)):
            self.image_processing_instance.stop_video_capture()

    def manage_signals(self):
        self.btn_start.clicked.connect(self.start_camera)
        self.btn_create_model.clicked.connect(self.create_directory)

    def create_directory(self):
        if(len(self.text_model.text()) != 0):
            # Create the model name
            self.models_path += self.text_model.text()
            # Create the directory with the same name
            os.mkdir(self.models_path)
            # Show message
            Utilities.show_message(title="Attention", message= f"Directory {self.text_model.text()} created successfully")
            self.models_path+= "/"
            self.start_change_handler()
        else:
             Utilities.show_message(title="Attention", message="The directory name is required")
    
    def load_directories(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.models_path)
        self.folders_tree.setModel(self.model)
        self.folders_tree.setRootIndex(self.model.index(self.models_path))

    def start_camera(self):
    
        if self.rdb_by_time.isChecked() and self.spin_by_time.value() != 0:

            self.image_processing_instance = VideoProcessing(self.lbl_image_result,
                capture_duration=self.spin_by_time.value(),
                path_to_save=self.models_path,
                type_capture='ByTime')
            
            self.image_processing_instance.start_video_capture()
             
        if self.rdb_by_quantity.isChecked() and self.spin_by_quantity.value() != 0:

            self.creation_progress.setMaximum(self.spin_by_quantity.value())
            
            self.image_processing_instance = VideoProcessing(self.lbl_image_result,
                path_to_save=self.models_path,
                total_images=self.spin_by_quantity.value(),
                type_capture='ByQuantity')
            
            self.image_processing_instance.start_video_capture()
      
    def start_change_handler(self):
        self.event_handler = ChangeHandler(self.creation_progress)
        self.observer = Observer()

        self.observer.schedule(self.event_handler, path=self.models_path, recursive=False)
        self.observer.start()


if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = ViewCreateModel()

    app.exec()
