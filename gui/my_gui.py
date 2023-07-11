import logging
import os
from time import sleep
from PyQt5.QtWidgets import (
    QMainWindow,
    QAction,
    QLineEdit,
    QMessageBox,
    QFileDialog,
    QInputDialog,
    QGraphicsScene,
    QGraphicsPixmapItem
)

from PyQt5 import uic
from PyQt5.QtGui import QIcon,QPixmap
from qasync import asyncSlot
from PyQt5.QtCore import Qt
from constants import CalculationConstants, FTPConstants
from controllers.ftp_session_controller import FTPSession

from controllers.telnet_controller import TelnetController
from controllers.ftp_controller import FTPController
from controllers.debug_console_controller import DebugConsoleController
from config.application_config import AppConfig

from gui.telnet_settings_dialog import TelnetSettingsDialog
from gui.ftp_settings_dialog import FTPSettingsDialog
from gui.log_handler import LogHandler

from tasks.lv5600_tasks import LV5600Tasks
from tasks.calculation_tasks import CalculationTasks


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("gui/resources/LV5600-Automation-GUI.ui", self)
        self.setWindowTitle("LV5600 Automation")
        self.setWindowIcon(QIcon("gui/resources/icon.svg"))

        # initiaize the application config
        self.app_config = AppConfig()

        # initialize the Telnet and FTP clients with values from the config
        self.telnet_client = TelnetController(
            self.app_config.get_telnet_address(),
            self.app_config.get_telnet_port(),
            self.app_config.get_telnet_username(),
            self.app_config.get_telnet_password(),
        )
        self.ftp_client = FTPController(
            self.app_config.get_ftp_address(),
            self.app_config.get_ftp_username(),
            self.app_config.get_ftp_password(),
        )
        self.debug_console_controller = DebugConsoleController()

        # initialize the log handler
        self.log_handler = LogHandler(self.textBrowser)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.log_handler)

        # set echo mode to Password for the password fields
        self.lineEdit_pwd.setEchoMode(QLineEdit.Password)

        # * binding of the menu bar actions to slots
        # find the actionTelnet_Settings and actionFTP_Settings actions and connect their triggered signals to slots
        self.actionTelnet_Settings = self.findChild(QAction, "actionTelnet_Settings")
        self.actionTelnet_Settings.triggered.connect(self.open_telnet_settings_dialog)  # type: ignore
        self.actionFTP_Settings = self.findChild(QAction, "actionFTP_Settings")
        self.actionFTP_Settings.triggered.connect(self.open_ftp_settings_dialog)  # type: ignore
        self.actionLocal_File_Path = self.findChild(QAction, "actionLocal_File_Path")
        self.actionLocal_File_Path.triggered.connect(self.open_local_file_path_dialog)  # type: ignore


        # todo - setup other GUI components and signal-slot connections
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_establish_connection.clicked.connect(self.establish_connection)
        self.pushButton_initialize_lv5600.clicked.connect(self.clicked_initialize_lv5600)
        self.pushButton_capture_n_send_bmp.clicked.connect(self.clicked_capture_n_send_bmp)
        self.pushButton_recall_preset.clicked.connect(self.clicked_recall_preset)
        self.pushButton_capture_n_classify_sat.clicked.connect(self.clicked_capture_n_classify_sat)

    def login(self):
        if (
            self.lineEdit_username.text() == "LV5600"
            and self.lineEdit_pwd.text() == "LV5600"
        ):
            # disable login related components
            self.lineEdit_username.setEnabled(False)
            self.lineEdit_pwd.setEnabled(False)
            self.pushButton_login.setEnabled(False)

            # enable establish connection related components
            self.pushButton_establish_connection.setEnabled(True)
        else:
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Invalid Username or Password")
            message.setIcon(QMessageBox.Critical)
            message.exec()

    @asyncSlot()
    async def establish_connection(self):
        try:
            logging.info("Establishing Telnet connection")
            logging.info("Telnet address: " + self.app_config.get_telnet_address())
            logging.info("Telnet port: " + str(self.app_config.get_telnet_port()))
            logging.info("Telnet username: " + self.app_config.get_telnet_username())
            logging.info("Telnet password: " + self.app_config.get_telnet_password())
            status = await self.telnet_client.connect()
            if not status:
                logging.error("Error establishing Telnet connection")
                return
            logging.info("Telnet connection established")

            login_status = await self.telnet_client.login()
            if not login_status:
                logging.error("Error logging in to Telnet")
                await self.telnet_client.close()
                return
            logging.info("Logged into Telnet successfully")

        except Exception as e:
            logging.error("Error establishing Telnet connection: " + str(e))
            await self.telnet_client.close()
            return

        try:
            if not self.debug_console_controller.activate():
                logging.error("Error activating debug console")
                return
            logging.info("Debug console activated")
        except Exception as e:
            logging.error("Error activating debug console: " + str(e))
            return

        # disable establish connection related components
        self.pushButton_establish_connection.setEnabled(False)

        # enable other components
        self.pushButton_initialize_lv5600.setEnabled(True)
        self.pushButton_auto_wb.setEnabled(True)
        self.pushButton_capture_n_classify_sat.setEnabled(True)
        self.pushButton_auto_adjust_sat.setEnabled(True)
        self.pushButton_recall_preset.setEnabled(True)
        self.pushButton_capture_n_send_bmp.setEnabled(True)
        self.pushButton_auto_adjust_n1_plus20.setEnabled(True)
        self.pushButton_auto_adjust_n1_minus20.setEnabled(True)
        self.textBrowser.setEnabled(True)
        self.graphicsView.setEnabled(True)
        self.label_graphics.setEnabled(True)

    def open_telnet_settings_dialog(self):
        # Create a new TelnetSettingsDialog
        dialog = TelnetSettingsDialog(self.app_config)
        logging.info("Telnet settings dialog created")
        # Show the dialog modally. If the user saves the settings, restart the telnet and ftp clients.
        if dialog.exec():
            logging.info("Telnet settings changed. Restarting Telnet and FTP clients")
            self.telnet_client = TelnetController(
                self.app_config.get_telnet_address(),
                self.app_config.get_telnet_port(),
                self.app_config.get_telnet_username(),
                self.app_config.get_telnet_password(),
            )

    def open_ftp_settings_dialog(self):
        # Create a new FTPSettingsDialog
        dialog = FTPSettingsDialog(self.app_config)
        logging.info("FTP settings dialog created")
        # Show the dialog modally. If the user saves the settings, restart the ftp client.
        if dialog.exec():
            logging.info("FTP settings changed. Restarting FTP client")
            self.ftp_client = FTPController(
                self.app_config.get_ftp_address(),
                self.app_config.get_ftp_username(),
                self.app_config.get_ftp_password(),
            )

    def open_local_file_path_dialog(self):
        # let the user select a local file path and write back to the config file
        local_file_path = QFileDialog.getExistingDirectory(
            self, "Select Local File Path"
        )
        if local_file_path:
            self.app_config.set_local_file_path(local_file_path)


    def display_image_and_title(self, pixmap, title):
        new_size = self.graphicsView.size()
        pixmap = pixmap.scaled(new_size, Qt.KeepAspectRatio)  # type: ignore

        # display the image
        scene = QGraphicsScene(self)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.graphicsView.setScene(scene)
        self.graphicsView.fitInView(item)

        # display the title
        self.label_graphics.setText(title)

    @asyncSlot()
    async def clicked_initialize_lv5600(self):
        logging.info("-------------------- Initializing LV5600 --------------------")
        await LV5600Tasks.initialize_lv5600(self.telnet_client)
        logging.info("-------------------- LV5600 Initialized --------------------")

    @asyncSlot()
    async def clicked_capture_n_send_bmp(self):
        logging.info("-------------------- Capturing and sending BMP --------------------")
        local_file_path = os.path.join(self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP)
        with FTPSession(self.ftp_client) as ftp_client:
            await LV5600Tasks.capture_n_send_bmp(self.telnet_client, ftp_client, local_file_path)
            # display in graphics view
            pixmap = QPixmap(local_file_path)
            self.display_image_and_title(pixmap, "Snapshot")
        logging.info("-------------------- BMP captured and sent --------------------")

    @asyncSlot()
    async def clicked_recall_preset(self):
        preset_number, ok = QInputDialog.getInt(self, "Recall Preset", "Enter Preset Number (1-60):", 1, 1, 60, 1)
        if ok:
            logging.info(f"-------------------- Recalling Preset {preset_number} --------------------")
            await LV5600Tasks.recall_preset(self.telnet_client, preset_number)
            logging.info(f"-------------------- Preset {preset_number} recalled --------------------")
        
    @asyncSlot()
    async def clicked_capture_n_classify_sat(self):
        logging.info("-------------------- Capturing and classifying SAT --------------------")
        local_file_path = os.path.join(self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP)
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)
            # capture an image
            await LV5600Tasks.capture_n_send_bmp(self.telnet_client, ftp_client, local_file_path)
            # preprocess the image
            mid_cyan_y_value = await CalculationTasks.preprocess_and_get_mid_cyan("SAT")
            logging.debug(f"Mid Cyan Y Value: {mid_cyan_y_value}")
            # get cursor and mv
            cursor, mv = CalculationTasks.get_cursor_and_mv(mid_cyan_y_value)
            logging.debug(f"Cursor: {cursor}, MV: {mv}")
            # classify SAT using mv 
            class_ = CalculationTasks.classify_mv_level(mv,CalculationConstants.TARGET_SATURATION_MV_VALUE)
            if class_ == "pass":
                class_ = "Just Saturated"
            elif class_ == "low":
                class_ = "Under Saturated"
            elif class_ == "high":
                class_ = "Over Saturated"
            
            # turn on scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)
            
            # display in graphics view
            pixmap = QPixmap(local_file_path)
            self.display_image_and_title(pixmap, f"SAT: {class_}")
        logging.info("-------------------- SAT captured and classified --------------------")