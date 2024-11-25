import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QPushButton, QWidget, QApplication, QGroupBox

from Views.view_create_model import ViewCreateModel
from Views.view_camera import ViewProductionCamera
from Views.view_compare_images import ViewCompareImages

class MainView(QWidget):
    # Constructor
    def __init__(self):
        super(MainView, self).__init__()

        # Call Draw components
        self.draw_components()
        self.manage_signals()
        self.disable_buttons()
    
    # Methods
    def draw_components(self):
        # Load template
        uic.loadUi('Templates/main_view.ui', self) 

        # Find Components
        self.btn_open_camera = self.findChild(QPushButton, 'btn_open_camera')
        self.btn_create_model = self.findChild(QPushButton, 'btn_create_model')
        self.btn_campare_images = self.findChild(QPushButton, 'btn_campare_images')
        self.btn_detect_contours = self.findChild(QPushButton, 'btn_detect_contours')
        self.btn_login = self.findChild(QPushButton, 'btn_login')

        self.groupBox_tools = self.findChild(QGroupBox, 'groupBox_tools')

    def manage_signals(self):
        self.btn_create_model.clicked.connect(self.open_view_create_model)
        self.btn_login.clicked.connect(self.enable_buttons)
        self.btn_open_camera.clicked.connect(self.open_view_production_camera)
        self.btn_campare_images.clicked.connect(self.open_view_compare_images)
    
    def open_view_create_model(self):
        self.view_create_model = ViewCreateModel()
        self.view_create_model.show()

    def open_view_production_camera(self):
        self.view_production_camera = ViewProductionCamera()
        self.view_production_camera.show()

    def open_view_compare_images(self):
        self.view_compare_images = ViewCompareImages()
        self.view_compare_images.show()


    def enable_buttons(self):
        self.btn_open_camera.setEnabled(True)
        self.btn_create_model.setEnabled(True)
        self.btn_campare_images.setEnabled(True)
        self.btn_detect_contours.setEnabled(True)

    def disable_buttons(self):
        self.btn_open_camera.setEnabled(False)
        self.btn_create_model.setEnabled(False)
        self.btn_campare_images.setEnabled(False)
        self.btn_detect_contours.setEnabled(False)

if __name__ == '__main__':

    app = QApplication(sys.argv)

    window = MainView()

    window.show()

    app.exec()