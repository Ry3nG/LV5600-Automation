from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import sys

class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()

        self.setWindowTitle("About")
        self.setFixedSize(400,300)

        layout = QVBoxLayout()

        label = QLabel("LV5600-OCB-Automation\n\nDeveloped by: Olympus Singapore Pte Ltd\n\nVersion: 1.0.0")
        layout.addWidget(label)

        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        layout.addWidget(closeButton)

        self.setLayout(layout)
