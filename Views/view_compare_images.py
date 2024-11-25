import os
import sys
from uuid import uuid4
from watchdog.observers import Observer
from PyQt6 import uic
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QFileSystemModel, QIcon, QGuiApplication, QAction, QPixmap
from PyQt6.QtWidgets import QPushButton, QApplication, QLabel, QLineEdit, QProgressBar, QComboBox, QTreeView, QWidget, QMenu

from . utilities.static_methods import Utilities
from . utilities.change_handler import ChangeHandler

from Views.utilities.video_processing import VideoProcessing
from Views.utilities.video_image_processing import VideoImageProcessing


class ViewCompareImages(QWidget):
    # Constructor
    def __init__(self):
        super(ViewCompareImages, self).__init__()

        # Properties
        self.full_path = None
        self.full_name = None
        self.image_processing_instance = None
        self.video_image_processing_instance = None
        self.full_directory_path = None
        self.expected_image_path = None

        # Settings
        json_settins = Utilities.load_json_settings()
        self.directories = json_settins['directories']['models']

        # Draw Components
        self.draw_components()
        self.load_directories()
        self.manage_signals()
        self.set_center_window()
        

    def draw_components(self):
        # load ui file
        uic.loadUi('Templates/viewCompareImages.ui', self)

        self.cbo_model = self.findChild(QComboBox, 'cbo_model')
        self.cbo_model.currentTextChanged.connect(self.on_text_changed)

        self.lbl_quantity = self.findChild(QLabel, 'lbl_quantity')
        self.lbl_model_name = self.findChild(QLabel, 'lbl_model_name')
        self.label_2 = self.findChild(QLabel, 'label_2')

        self.text_images_to_create = self.findChild(QLineEdit, 'text_images_to_create')

        self.btn_execute = self.findChild(QPushButton, 'btn_execute')
        self.btn_create_directory = self.findChild(QPushButton, 'btn_create_directory')
        self.btn_create_directory.clicked.connect(self.create_directory)
        self.progressBar_images = self.findChild(QProgressBar, 'progressBar_images')

        self.tree_golden_images = self.findChild(QTreeView, 'tree_golden_images')
        self.tree_result_images = self.findChild(QTreeView, 'tree_result_images')

        self.lbl_screen = self.findChild(QLabel, 'lbl_screen')

    def closeEvent(self, event):
        if(isinstance(self.video_image_processing_instance, VideoImageProcessing)):
            self.video_image_processing_instance.stop_video_image_processing()

    def set_center_window(self):
        qr = self.geometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def manage_signals(self):
        self.btn_execute.clicked.connect(self.compare_image_on_time)

        # Set Properties and manage events QTreeView Golden Images
        self.tree_golden_images.clicked.connect(self.on_item_clicked)
        self.tree_golden_images.installEventFilter(self)
        self.tree_golden_images.selectionModel().selectionChanged.connect(self.selection_changed_golden_images)
        self.tree_golden_images.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_golden_images.customContextMenuRequested.connect(self.open_context_menu)

        # Set Properties and manage events QTreeView Result Images
        self.tree_result_images.clicked.connect(self.on_item_clicked)
        self.tree_result_images.installEventFilter(self)

    def load_directories(self):
        self.dic_directories = {f.path: f.name for f in os.scandir(self.directories) if f.is_dir()}
        for item in self.dic_directories.values():
            self.cbo_model.addItem(item)

    def on_text_changed(self, text):
        for key , value in self.dic_directories.items():
            if text == value:
                self.lbl_model_name.setText(text)
                self.full_path = key
                
        self.load_selected_directory(self.full_path)

    def load_selected_directory(self, path):
        self.model = QFileSystemModel()
        self.model.setRootPath(path)
        self.tree_golden_images.setModel(self.model)
        self.tree_golden_images.setRootIndex(self.model.index(path))

        items = os.listdir(path)
        counter = sum(1 for item in items if os.path.isfile(os.path.join(path, item)))

        self.lbl_quantity.setText(str(counter))
        self.text_images_to_create.setText(str(counter))
        self.progressBar_images.setMaximum(counter)

        self.tree_golden_images.selectionModel().selectionChanged.connect(self.selection_changed_golden_images)

    def create_directory(self):

        directory_path = self.full_path
        directory_name = self.generate_name()

        self.full_directory_path = "/".join([directory_path, directory_name])
        os.mkdir(self.full_directory_path)
        self.load_result_directory(self.full_directory_path)
        self.start_change_handler()

    def load_result_directory(self, file_path):
        self.result_model = QFileSystemModel()
        self.result_model.setRootPath(file_path)
        self.tree_result_images.setModel(self.result_model)
        self.tree_result_images.setRootIndex(self.result_model.index(file_path))
        self.tree_result_images.selectionModel().selectionChanged.connect(self.selection_changed_result_images)

    def generate_name(self)->str:
        directory_name = 'Directory'
        identifier = str(uuid4())[:10]
        string_result = "-".join([directory_name, identifier])

        return string_result
    
    def start_camera(self):
        self.full_directory_path += '/'

        if self.text_images_to_create != '':
            self.image_processing_instance = VideoProcessing(
                lbl_camera=self.lbl_screen,
                path_to_save=self.full_directory_path,
                total_images=int(self.text_images_to_create.text()),
                type_capture='ByQuantity'
            )

            self.image_processing_instance.start_video_capture()
            print('Ha finalizado la creación de archivos')

    def start_change_handler(self):
        self.event_handler = ChangeHandler(self.progressBar_images)
        self.observer = Observer()

        self.observer.schedule(self.event_handler, path=self.full_directory_path, recursive=False)
        self.observer.start()

    def on_item_clicked(self, index):
        file_path = self.model.filePath(index)
        self.expected_image_path = file_path

        if os.path.isfile(file_path):
            selected_image = QPixmap(file_path)
            self.lbl_screen.setPixmap(selected_image)

    def eventFilter(self, source, event) -> bool:
    # Filtrar eventos de teclado solo si son de QTreeView y son pulsaciones de teclas
        if event.type() == QEvent.Type.KeyPress and (source == self.tree_golden_images or source == self.tree_result_images):
        # Solo interesan las teclas arriba y abajo
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                return False

        return super().eventFilter(source, event)
    
    def selection_changed_golden_images(self, selected, deselected):
        # Se obtiene el indice actual
        index = self.tree_golden_images.currentIndex()

        if index.isValid():
            # Se obtiene la ruta de la imagen seleccionada
            file_path = self.model.filePath(index)

            if os.path.isfile(file_path):
                # Se crea un objeto QPixmap
                selected_image = QPixmap(file_path)
                self.expected_image_path = file_path
                # Se muestra la imagen en el QLabel
                self.lbl_screen.setPixmap(selected_image)

    def selection_changed_result_images(self, selected, deselected):
        index = self.tree_result_images.currentIndex()

        if index.isValid():
            file_path = self.result_model.filePath(index)
            
            if os.path.isfile(file_path):
                selected_image = QPixmap(file_path)
                self.lbl_screen.setPixmap(selected_image)

    def open_context_menu(self, position: QPoint):
        
        index = self.tree_golden_images.indexAt(position)

        if not index.isValid():
            return
        file_path = self.model.filePath(index)

        # Se revisa que sea un directorio
        if os.path.isdir(file_path):
            # Se crea el Menu contextual
            menu = QMenu()
            select_directory = QAction("Seleccionar Directorio", self)

            # Se agregan las opciones al menu
            menu.addAction(select_directory)
            # Se conectan las acciones con los metodos
            select_directory.triggered.connect(lambda: self.load_result_directory(file_path))
            # Se muestra el menu contextual
            menu.exec(self.tree_golden_images.viewport().mapToGlobal(position))
    
    def compare_image_on_time(self):

        if self.expected_image_path != '':
            self.video_image_processing_instance = VideoImageProcessing(
                self.expected_image_path,
                self.lbl_screen
            )
        
        self.video_image_processing_instance.start_video_image_processing()

if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    window = ViewCompareImages()

    window.show()

    app.exec()

