import logging
import typing
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QWidget

class TargetToleranceDialog(QDialog):
    # target tolerance involves 3 params
        # 1. target tolerance : 0% to 100%
        # 2. flatness_check_pixel: 0 pixel to 200 pixel
        # 3. flatness_check_sv_threshold: 0.0 to 100.0
    def __init__(self, app_config):
        super(TargetToleranceDialog, self).__init__()

        self.app_config = app_config
        logging.debug("TargetToleranceDialog: app_config: {}".format(self.app_config))

        # create widgets, using spinbox 
        self.target_tolerance_spinbox = QtWidgets.QDoubleSpinBox()
        self.target_tolerance_spinbox.setRange(0,100)
        self.target_tolerance_spinbox.setSingleStep(0.1)
        self.target_tolerance_spinbox.setValue(self.app_config.get_target_tolerance()*100)
        self.target_tolerance_spinbox.setDecimals(1)
        self.target_tolerance_spinbox.setSuffix("%")
        self.flatness_check_pixel_spinbox = QtWidgets.QSpinBox()
        self.flatness_check_pixel_spinbox.setRange(0, 200)
        self.flatness_check_pixel_spinbox.setSingleStep(1)
        self.flatness_check_pixel_spinbox.setValue(int(self.app_config.get_flatness_check_pixel()))
        self.flatness_check_sv_threshold_spinbox = QtWidgets.QDoubleSpinBox()
        self.flatness_check_sv_threshold_spinbox.setRange(0.0, 100.0)
        self.flatness_check_sv_threshold_spinbox.setSingleStep(0.1)
        self.flatness_check_sv_threshold_spinbox.setValue(self.app_config.get_flatness_check_sv_threshold())
        self.flatness_check_sv_threshold_spinbox.setDecimals(1)
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        # set title
        self.setWindowTitle("Target Tolerance Settings")

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Target Tolerance:"))
        layout.addWidget(self.target_tolerance_spinbox)
        layout.addWidget(QLabel("Flatness Check Pixel:"))
        layout.addWidget(self.flatness_check_pixel_spinbox)
        layout.addWidget(QLabel("Flatness Check SV Threshold:"))
        layout.addWidget(self.flatness_check_sv_threshold_spinbox)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)

        # Connect signals and slots
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.close)

    def save_settings(self):
        # update app_config
        self.app_config.set_target_tolerance(float(self.target_tolerance_spinbox.value()/100))
        self.app_config.set_flatness_check_pixel(float(self.flatness_check_pixel_spinbox.value()))
        self.app_config.set_flatness_check_sv_threshold(float(self.flatness_check_sv_threshold_spinbox.value()))

        # update config.ini
        self.app_config.save_config_to_file()

        # close dialog
        self.accept()

    
