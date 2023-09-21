import logging
import os
import time
import typing
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QMessageBox,
    QWidget,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFileDialog,
    QInputDialog,
)


from PyQt5 import QtCore, uic
from PyQt5.QtGui import QPixmap
from qasync import asyncSlot
from config.application_config import AppConfig
from controllers.debug_console_controller import DebugConsoleController
from controllers.ftp_controller import FTPController
from controllers.telnet_controller import TelnetController
from controllers.waveform_image_analysis_controller import (
    WaveformImageAnalysisController,
)
from gui.ftp_settings_dialog import FTPSettingsDialog
from gui.log_handler import LogHandler
from gui.resources import resources_rc
import sys
from gui.telnet_settings_dialog import TelnetSettingsDialog

from tasks.connection_tasks import ConnectionTask
from tasks.lv5600_tasks import LV5600Tasks


class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUI()
        self.setupEvents()

    def setupUI(self):
        self.loadUIFile("LV5600-Automation-OCB-Login-GUI.ui")
        self.olympus_logo.setStyleSheet(
            "border-image:url(:/image/Olympus_Corporation_logo.svg.png); border-top-left-radius: 50px; padding-top: 56.25%; width: 100%;"
        )

    def setupEvents(self):
        self.pushButton_submit.clicked.connect(self.login)

    def loadUIFile(self, ui_file_name):
        application_path = self.getApplicationPath()
        ui_file_path = os.path.join(application_path, "resources", ui_file_name)
        uic.loadUi(ui_file_path, self)

    def getApplicationPath(self):
        return (
            sys._MEIPASS
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__))
        )

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
        self.setupControllers()
        self.setupUI()
        self.setupLogging()
        self.setupEvents()

    def setupUI(self):
        self.loadUIFile("LV5600-Automation-OCB-GUI-2.0.ui")
        self.setupToolBoxView()
        self.setupWelcomeImage()
        self.updateCurrentSettings()

    def setupToolBoxView(self):
        self.ToolBox.setCurrentIndex(0)

    def setupWelcomeImage(self):
        self.scene = QGraphicsScene()
        logo_path = os.path.join(
            self.getApplicationPath(), "resources", "Olympus_Corporation_logo.svg.png"
        )
        pixmap = QPixmap(logo_path)
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.fitInView(self.scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        self.graphicsView.scale(2, 2)

    def setupControllers(self):
        self.app_config_handler = AppConfig()
        self.telnet_clinet = TelnetController(
            self.app_config_handler.get_telnet_address(),
            self.app_config_handler.get_telnet_port(),
            self.app_config_handler.get_telnet_username(),
            self.app_config_handler.get_telnet_password(),
        )

        self.ftp_client = FTPController(
            self.app_config_handler.get_ftp_address(),
            self.app_config_handler.get_ftp_username(),
            self.app_config_handler.get_ftp_password(),
        )

        self.debug_console_controller = DebugConsoleController()

        self.wfm_image_analysis_controller = WaveformImageAnalysisController()

    def setupLogging(self):
        self.log_handler = LogHandler(self.textBrowser_console)
        self.log_handler.setup_application_logging()

    def loadUIFile(self, ui_file_name):
        application_path = self.getApplicationPath()
        ui_file_path = os.path.join(application_path, "resources", ui_file_name)
        uic.loadUi(ui_file_path, self)

    def getApplicationPath(self):
        return (
            sys._MEIPASS
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.abspath(__file__))
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Message",
            "Are you sure to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.telnet_clinet.close()
            self.ftp_client.close()
            event.accept()
        else:
            event.ignore()

    def setupEvents(self):
        # Page 1 - Setup and Initialization
        self.pushButton_establish_connection.clicked.connect(self.establishConnection)
        self.pushButton_initialize_lv5600.clicked.connect(self.initializeLV5600)

        self.pushButton_edit_telnet_settings.clicked.connect(self.editTelnetSettings)
        self.pushButton_edit_ftp_settings.clicked.connect(self.editFTPSettings)
        self.pushButton_edit_local_file_path.clicked.connect(self.editLocalFilePath)
        self.pushButton_edit_target_tolerance.clicked.connect(self.editTargetTolerance)
        self.pushButton_edit_line_number.clicked.connect(self.editLineNumber)

        self.app_config_handler.settings_changed.connect(self.updateCurrentSettings)

        # Page 2 - OCB Control
        self.pushButton_deliver_mask_mode.clicked.connect(self.deliverMaskMode)
        self.pushButton_deliver_agc_setting.clicked.connect(self.deliverAgcSetting)
        self.pushButton_deliver_light_level.clicked.connect(self.deliverLightLevel)

        # Page 3 - Dynamic Range Automation

    def updateCurrentSettings(self):
        current_settings = self.app_config_handler.get_current_settings()
        self.textBrowser_current_settings.setText(current_settings)

    @asyncSlot()
    async def establishConnection(self):
        logging.info(
            "-------------------- Establishing Connection --------------------"
        )
        # time the operation
        tic = time.time()
        try:
            await ConnectionTask.connect_to_telnet(self.telnet_clinet)
        except Exception as e:
            logging.error(f"Error while establishing connection: {str(e)}")
            return
        toc = time.time()
        logging.info("-------------------- Connection Established --------------------")
        logging.info(f"Time Elapsed: {toc - tic} seconds")

    @asyncSlot()
    async def initializeLV5600(self):
        logging.info("-------------------- Initializing LV5600 --------------------")
        tic = time.time()
        try:
            await LV5600Tasks.initialize_lv5600(self.telnet_clinet)
        except Exception as e:
            logging.error(f"Error while initializing LV5600: {str(e)}")
            return
        toc = time.time()
        logging.info("-------------------- LV5600 Initialized --------------------")
        logging.info(f"Time Elapsed: {toc - tic} seconds")

    def editTelnetSettings(self):
        self.telnet_settings_dialog = TelnetSettingsDialog(self.app_config_handler)
        self.telnet_settings_dialog.exec_()
        # update telnet client
        self.telnet_client = TelnetController(
            self.app_config_handler.get_telnet_address(),
            self.app_config_handler.get_telnet_port(),
            self.app_config_handler.get_telnet_username(),
            self.app_config_handler.get_telnet_password(),
        )

    def editFTPSettings(self):
        self.ftp_settings_dialog = FTPSettingsDialog(self.app_config_handler)
        self.ftp_settings_dialog.exec_()
        # update ftp client
        self.ftp_client = FTPController(
            self.app_config_handler.get_ftp_address(),
            self.app_config_handler.get_ftp_username(),
            self.app_config_handler.get_ftp_password(),
        )

    def editLocalFilePath(self):
        local_file_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if local_file_path:
            self.app_config_handler.set_local_file_path(local_file_path)
            self.app_config_handler.save_config_to_file()

    def editTargetTolerance(self):
        current_value = self.app_config_handler.get_target_tolerance()
        current_value = float(current_value)
        target_tolerance, ok = QInputDialog.getDouble(
            self, "Target Tolerance", "Enter Target Tolerance:", current_value, 0, 1, 2
        )
        if ok:
            self.app_config_handler.set_target_tolerance(target_tolerance)
            self.app_config_handler.save_config_to_file()

    def editLineNumber(self):
        current_value = self.app_config_handler.get_line_number()
        current_value = int(current_value)
        line_number, ok = QInputDialog.getInt(
            self, "Line Number", "Enter Line Number:", current_value, 1, 10000, 1
        )
        if ok:
            self.app_config_handler.set_line_number(line_number)
            self.app_config_handler.save_config_to_file()

    def deliverMaskMode(self):
        selected_mode = self.comboBox_mask_mode.currentText()
        logging.info(f"Selected Mask Mode: {selected_mode}")

        tic = time.time()
        if selected_mode == "Mask On":
            self.debug_console_controller.set_mask_mode("ON")
        elif selected_mode == "Mask Off":
            self.debug_console_controller.set_mask_mode("OFF")
        elif selected_mode == "Mask Cross":
            self.debug_console_controller.set_mask_mode("CROSS")
        toc = time.time()

        logging.info("-------------------- Mask Mode Delivered --------------------")
        logging.info(f"Time Elapsed: {toc - tic} seconds")

    def deliverAgcSetting(self):
        selected_setting = self.comboBox_agc_setting.currentText()
        logging.info(f"Selected AGC Setting: {selected_setting}")
        
        tic = time.time()
        if selected_setting == "WLI Mode":
            self.debug_console_controller.set_AGC_mode("WLI")
        elif selected_setting == "NBI Mode":
            self.debug_console_controller.set_AGC_mode("NBI")
        elif selected_setting == "RDI Mode":
            self.debug_console_controller.set_AGC_mode("RDI")
        elif selected_setting == "AGC On":
            self.debug_console_controller.set_AGC_mode("ON")
        elif selected_setting == "AGC Off":
            self.debug_console_controller.set_AGC_mode("OFF")

        toc = time.time()
        logging.info("-------------------- AGC Setting Delivered --------------------")
        logging.info(f"Time Elapsed: {toc - tic} seconds")


    def deliverLightLevel(self):
        selected_light_level = self.spinBox_light_level.value()
        logging.info(f"Selected Light Level: {selected_light_level}")
        self.debug_console_controller.set_light_level(selected_light_level)
