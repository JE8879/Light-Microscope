import sys
import cv2
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
from skimage.metrics import structural_similarity as compare_ssim


class VideoComparison(QThread):
    # Signals
    change_pixmap_signal = pyqtSignal(QPixmap)
    # Constructor 
    def __init__(self,
        expected_image_path = None):
        super(VideoComparison, self).__init__()

        # Properties
        self.expected_image_path = expected_image_path
        self.run_flag = True
        self.cap = None
    
    @pyqtSlot()
    def stop(self):
        self.run_flag = False
        self.wait()

    def run(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        
        self.capture_by_static_image()
        self.cap.release()


    def capture_by_static_image(self):

        self.ref_image = cv2.imread(self.expected_image_path, cv2.IMREAD_GRAYSCALE)
        _, umbral_image_one = cv2.threshold(self.ref_image, 67, 127, cv2.THRESH_TOZERO_INV)
      

        while(self.run_flag):
            ret, cv_img = self.cap.read()
            if ret:
             
                gray_frame = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                (score, diff) = compare_ssim(self.ref_image, gray_frame, full=True)
                diff = (diff * 255).astype("uint8")
                diff_box = cv2.merge([diff, diff, diff])


                # Threshold the difference image, followed by finding contours to
                # obtain the regions of the two input images that differ
                thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contours = contours[0] if len(contours) == 2 else contours[1]
                
                
                mask = np.zeros(cv_img.shape, dtype='uint8')
                filled_after = cv_img.copy()

                for c in contours:
                    area = cv2.contourArea(c)
                    if area > 40:
                        x, y, w, h = cv2.boundingRect(c)
                        cv2.rectangle(cv_img, (x, y), (x + w, y + h), (36,255,12),2)
                        cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36,255,12),2)
                        cv2.drawContours(mask, [c], 0, (255, 255, 255), -1)
                        cv2.drawContours(filled_after, [c], 0, (255, 255, 255), -1)

                cv2.putText(cv_img, f'SSIM: {score:.2f}%', (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                pixmap_image = self.convert_cv2_image_to_q_pixmap(cv_img)
                self.change_pixmap_signal.emit(pixmap_image)

    def convert_cv2_image_to_q_pixmap(self, MatLike):
        rgb_image = cv2.cvtColor(MatLike, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap_image = QPixmap.fromImage(q_image)
        return pixmap_image


    

