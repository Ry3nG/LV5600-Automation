import os
import typing
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QWidget, QGraphicsScene, QGraphicsPixmapItem


from PyQt5 import QtCore, uic
from PyQt5.QtGui import QPixmap
from gui.resources import resources_rc
import sys

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        
        #determine if he application is a script file or frozen exe
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        ui_file_path = os.path.join(application_path, "resources","LV5600-Automation-OCB-Login-GUI.ui")
        uic.loadUi(ui_file_path, self)
        
        self.pushButton_submit.clicked.connect(self.login)
        self.olympus_logo.setStyleSheet("border-image:url(:/image/Olympus_Corporation_logo.svg.png); border-top-left-radius: 50px; padding-top: 56.25%; width: 100%;")

    def login(self):
        username = self.lineEdit_username.text()
        password = self.lineEdit_pwd.text()
        
        if username == "LV5600" and password == "LV5600":
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login", "Login Failed")  

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        #determine if he application is a script file or frozen exe
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        ui_file_path = os.path.join(application_path, "resources","LV5600-Automation-OCB-GUI-2.0.ui")
        uic.loadUi(ui_file_path, self)
        self.ToolBox.setCurrentIndex(0)
        self.scene = QGraphicsScene()
        logo_path = os.path.join(application_path, "resources","Olympus_Corporation_logo.svg.png")
        pixmap = QPixmap(logo_path)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.graphicsView.scale(2, 2)

