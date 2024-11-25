import cv2
import time
import numpy as np
from uuid import uuid4
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot

class VideoCapture(QThread):
    
    # Signals
    # change_pixmap_signal = pyqtSignal(np.ndarray)
    change_pixmap_signal = pyqtSignal(QPixmap)

    # Constructor
    def __init__(self,
        parent=None, 
        type_capture = None,
        path_to_save = None,
        capture_duration = None,
        total_images = None):
        super(VideoCapture, self).__init__(parent)

        # Properties
        self._run_flag = True
        self.path =path_to_save
        self._list_images = []
        self.type_capture = type_capture
        self.capture_duration = capture_duration
        self.total_images = total_images
        self.var = 0

        self._cap = None

    @pyqtSlot()
    def stop(self):
        self._run_flag = False
        self.wait()

    def run(self):
        self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self._cap.set(cv2.CAP_PROP_FPS, 60)

        if(self.type_capture == 'ByTime'):
            self.capture_by_time()

        if(self.type_capture == 'ByQuantity'):
            self.capture_by_quantity()

        if(self.type_capture == 'General'):
            self.capture_general()

        self._cap.release()

    def capture_general(self):

        while(self._run_flag):
            ret, cv_img = self._cap.read()
            if ret:
                pixmap_image = self.convert_cv2_image_to_q_pixmap(cv_img)
                self.change_pixmap_signal.emit(pixmap_image)
    
    def capture_by_time(self):
        start_time = time.time()
      
        while(int(time.time() - start_time) < self.capture_duration):
            ret, cv_img = self._cap.read()
            if ret:
                pixmap_image = self.convert_cv2_image_to_q_pixmap(cv_img)
                self.change_pixmap_signal.emit(pixmap_image)
                self._list_images.append(pixmap_image)

        for item in self._list_images:
            self.save_images(item, self.path)
        
        self._list_images = []

    def capture_by_quantity(self):
        image_counter = 0

        while image_counter < self.total_images:
            ret, cv_img = self._cap.read()
            if ret:
                pixmap_image = self.convert_cv2_image_to_q_pixmap(cv_img)
                self.change_pixmap_signal.emit(pixmap_image)
                self._list_images.append(pixmap_image)

                image_counter +=1
        for image in self._list_images:
            self.save_images(image, self.path)

        self._list_images = []

    def convert_cv2_image_to_q_pixmap(self, MatLike):
        rgb_image = cv2.cvtColor(MatLike, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap_image = QPixmap.fromImage(q_image)
        return pixmap_image
    
    def save_images(self, pixmap_image, path):
        path += self.generate_image_name()
        path += ".png"
        pixmap_image.save(path, "PNG")

    def generate_image_name(self):
        return str(uuid4())
    
    def execute_only_one(self):
        if(self.var == 0):
            self.var +=1
        else:
            return