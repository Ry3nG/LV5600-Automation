from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    QGraphicsScene,
    QGraphicsPixmapItem,
)

class DialogHandler():
    def __init__(self):
        self.widget_type = None
        self.title = None
        self.text = None
        self.icon = None
    
    def show_error_dialog(self, text):
        self.widget_type = QMessageBox
        self.title = "Error"
        self.text = text
        self.icon = QMessageBox.Critical
        self.show_dialog()

    def show_dialog(self):
        if self.widget_type is None:
            raise Exception("Dialog type not set")
        if self.title is None:
            raise Exception("Dialog title not set")
        if self.text is None:
            raise Exception("Dialog text not set")
        if self.icon is None:
            raise Exception("Dialog icon not set")
        
        msg = self.widget_type()
        msg.setWindowTitle(self.title)
        msg.setText(self.text)
        msg.setIcon(self.icon)
        msg.exec_()