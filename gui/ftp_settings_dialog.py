import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QWidget

class FTPSettingsDialog(QDialog):
    def __init__(self, app_config):
        super(FTPSettingsDialog, self).__init__()

        self.app_config = app_config

        # Create widgets
        self.host_line_edit = QLineEdit(self.app_config.get_ftp_address())
        self.username_line_edit = QLineEdit(self.app_config.get_ftp_username())
        self.password_line_edit = QLineEdit(self.app_config.get_ftp_password())
        self.password_line_edit.setEchoMode(QLineEdit.Password)
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Host:"))
        layout.addWidget(self.host_line_edit)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_line_edit)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_line_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect signals and slots
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.close) # type: ignore # close dialog
        
    def save_settings(self):
        # update app_config
        self.app_config.set_ftp_address(self.host_line_edit.text())
        self.app_config.set_ftp_username(self.username_line_edit.text())
        self.app_config.set_ftp_password(self.password_line_edit.text())

        # update config.ini
        self.app_config.save_config_to_file()

        # close dialog
        self.close()
        