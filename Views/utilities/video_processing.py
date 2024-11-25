import sys
import cv2
import time
import numpy as np
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from skimage.metrics import structural_similarity

from .video_capture import VideoCapture

class VideoProcessing(VideoCapture):
    # Constructor
    def __init__(self, 
        lbl_camera=None, 
        object_name=None, 
        capture_duration=None,
        path_to_save=None,
        type_capture=None,
        total_images=None):
        
        super(VideoProcessing, self).__init__()
        
        # Properties
        self._image_path = None
        self.lbl_camera = lbl_camera
        self.object_name = object_name
        self.capture_duration = capture_duration
        self.path_to_save = path_to_save
        self.type_capture = type_capture
        self.total_images = total_images
        self.list_images = []
        
    def start_video_capture(self):
        self.video_capture_instance = VideoCapture( 
            type_capture=self.type_capture, 
            path_to_save=self.path_to_save, 
            capture_duration=self.capture_duration,
            total_images=self.total_images
            )
        
        self.video_capture_instance.change_pixmap_signal.connect(self.update_image)
        self.video_capture_instance.start()

    @pyqtSlot(QPixmap)
    def update_image(self, pixmap_image):
        self.lbl_camera.setScaledContents(True)
        self.lbl_camera.setPixmap(pixmap_image)


    def stop_video_capture(self):
        self.video_capture_instance.stop()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    instance = VideoProcessing()

    sys.exit(app.exec())