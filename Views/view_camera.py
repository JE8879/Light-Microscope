import sys
from PyQt6 import uic
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QLabel, QApplication, QWidget, QTabWidget

from .utilities.video_processing import VideoProcessing

class ViewProductionCamera(QWidget):
    # Constructor
    def __init__(self):
        super(ViewProductionCamera, self).__init__()

        # Properties
        self.image_processing_instance = None

        self.draw_components()
        self.center_window()
        self.start_camera()

    def draw_components(self):
        # Load template
        uic.loadUi('Templates/viewCamera.ui', self)

        self.tab_container = self.findChild(QTabWidget, 'tab_container')
        self.lbl_screen = self.findChild(QLabel, 'lbl_screen')

    def start_camera(self):
        self.image_processing_instance = VideoProcessing(
            lbl_camera=self.lbl_screen,
            type_capture='General'
        )

        self.image_processing_instance.start_video_capture()

    def closeEvent(self, event):
        if(isinstance(self.image_processing_instance , VideoProcessing)):
            self.image_processing_instance.stop_video_capture()

    def center_window(self):
        qr = self.geometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = ViewProductionCamera()

    app.exec()