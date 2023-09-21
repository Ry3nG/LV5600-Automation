from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QGraphicsView
from PyQt5.QtGui import QPixmap, QImage
import os,sys
from PyQt5.QtCore import Qt


class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        self.setWindowTitle("About")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Load the Olympus logo image
        logo_path = os.path.join(
            self.getApplicationPath(), "resources", "Olympus_Corporation_logo.svg.png"
        )
        logo_image = QImage(logo_path)
        # Resize the logo to fit a specific size
        logo_pixmap = QPixmap.fromImage(logo_image).scaled(200, 100, aspectRatioMode= Qt.KeepAspectRatio)
        logo_label = QLabel()
        logo_label.setPixmap(logo_pixmap)
        layout.addWidget(logo_label)

        label = QLabel("LV5600-OCB-Automation\n\nDeveloped by: Olympus Singapore Pte Ltd\n\nVersion: 2.0.2309")
        layout.addWidget(label)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)

        self.setLayout(layout)
    
    def getApplicationPath(self):
        return (
            sys._MEIPASS
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__))
        )