import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import pyqtSlot

from . video_image_comparation import VideoComparison

class VideoImageProcessing(VideoComparison):
    # Constructor
    def __init__(self,
        expected_image_path = None,
        label_container = None):
        super(VideoImageProcessing, self).__init__()

        # Properties
        self.expected_image_path = expected_image_path
        self.label_container = label_container
    
    def start_video_image_processing(self):

        self.video_image_processing_instance = VideoComparison(
            expected_image_path=self.expected_image_path
        )

        self.video_image_processing_instance.change_pixmap_signal.connect(self.update_image)
        self.video_image_processing_instance.start()

    @pyqtSlot(QPixmap)
    def update_image(self, pixmap_image):
        self.label_container.setScaledContents(True)
        self.label_container.setPixmap(pixmap_image)


    def stop_video_image_processing(self):
        self.video_image_processing_instance.stop()

if __name__ == '__main__':

    app = QApplication(sys.argv)

    instance = VideoImageProcessing()

    sys.exit(app.exec())