from watchdog.events import FileSystemEventHandler
from PyQt6.QtCore import pyqtSignal, QObject

class ChangeHandler(FileSystemEventHandler, QObject):
    # Signals
    progress_signal = pyqtSignal(int)

    # Constructor
    def __init__(self, 
        progressbar = None):
        super(ChangeHandler, self).__init__()

        # Properties
        self.items_in_folder = 0
        self.progressbar = progressbar

        # Señal para actualizar el progressbar
        self.progress_signal.connect(self.update_progress)

    def on_created(self, event):
        # print(f'Archivo creado: {event.src_path}')

        if(event.src_path):
            self.items_in_folder += 1
            
            self.progress_signal.emit(self.items_in_folder)

    def update_progress(self, value):
        self.progressbar.setValue(value)
     