from functools import partial
import logging
import os
import sys
from time import sleep
import numpy as np


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

from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap
from qasync import asyncSlot
from PyQt5.QtCore import Qt
from Constants import CalculationConstants, FTPConstants
from controllers.ftp_session_controller import FTPSession

from controllers.telnet_controller import TelnetController
from controllers.ftp_controller import FTPController
from controllers.debug_console_controller import DebugConsoleController
from controllers.waveform_image_analysis_controller import (
    WaveformImageAnalysisController,
)

from config.application_config import AppConfig

from gui.about_dialog import AboutDialog
from gui.telnet_settings_dialog import TelnetSettingsDialog
from gui.ftp_settings_dialog import FTPSettingsDialog
from gui.log_handler import LogHandler
from gui.dialog_handler import DialogHandler

from tasks.lv5600_tasks import LV5600Tasks
from tasks.connection_tasks import ConnectionTask


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()

        # determine if the application is a script file or frozen exe
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS  # type: ignore
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))

        ui_file_path = os.path.join(
            application_path, "resources", "LV5600-Automation-GUI.ui"
        )
        uic.loadUi(ui_file_path, self)

        # Apply stylesheet
        self.setStyleSheet(
            """
            QWidget {
                font-size: 10px;
            }
            QPushButton {
                background-color: #b1b1b1;
                color: #333;
            }
            QPushButton:disabled {
                background-color: #d3d3d3;
                color: #888;
            }
            QLabel#label_graphics {
                font-size: 24px;
            }
            QObject#textBrowser {
                font-size: 12px;
            }
            """
        )

        self.setWindowTitle("LV5600-OCB-Automation")
        self.setWindowIcon(
            QIcon(os.path.join(application_path, "resources", "icon.ico"))
        )
        self.progressBar.setValue(0)

        # initiaize the application config
        self.app_config = AppConfig()

        self.dialog_handler = DialogHandler()

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

        self.waveform_image_analysis_controller = WaveformImageAnalysisController()

        self.wb_n1_value = -1

        # initialize the log handler
        self.log_handler = LogHandler(self.textBrowser)
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        self.log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.log_handler)

        # set echo mode to Password for the password fields
        self.lineEdit_pwd.setEchoMode(QLineEdit.Password)

        self.actionTelnet_Settings = self.findChild(QAction, "actionTelnet_Settings")
        self.actionTelnet_Settings.triggered.connect(self.open_telnet_settings_dialog)  # type: ignore
        self.actionFTP_Settings = self.findChild(QAction, "actionFTP_Settings")
        self.actionFTP_Settings.triggered.connect(self.open_ftp_settings_dialog)  # type: ignore
        self.actionLocal_File_Path = self.findChild(QAction, "actionLocal_File_Path")
        self.actionLocal_File_Path.triggered.connect(self.open_local_file_path_dialog)  # type: ignore
        self.actionEdit_target_tolerance = self.findChild(
            QAction, "actionEdit_target_tolerance"
        )
        self.actionEdit_target_tolerance.triggered.connect(self.open_target_tolerance_dialog)  # type: ignore
        self.actionEdit_Saturation_Target_mV = self.findChild(
            QAction, "actionEdit_Saturation_Target_mV"
        )
        self.actionEdit_Saturation_Target_mV.triggered.connect(self.open_saturation_target_dialog)  # type: ignore
        self.actionEdit_Oversaturate_Threshold.triggered.connect(self.open_oversaturate_threshold_dialog)  # type: ignore
        self.actionEdit_Line_Number.triggered.connect(self.open_line_number_dialog)  # type: ignore
        self.actionAbout.triggered.connect(self.show_about_dialog)  # type: ignore
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_establish_connection.clicked.connect(self.establish_connection)
        self.pushButton_initialize_lv5600.clicked.connect(
            self.clicked_initialize_lv5600
        )
        self.pushButton_capture_n_send_bmp.clicked.connect(
            self.clicked_capture_n_send_bmp
        )
        self.pushButton_capture_sat_value.clicked.connect(
            self.clicked_capture_sat_value
        )
        self.pushButton_capture_n_classify_sat.clicked.connect(
            self.clicked_capture_n_classify
        )
        self.pushButton_auto_wb.clicked.connect(self.clicked_auto_wb)
        self.pushButton_auto_adjust_sat.clicked.connect(self.clicked_auto_adjust_sat)
        self.pushButton_SAT_mode.clicked.connect(self.clicked_sat_mode)
        self.pushButton_mask_mode.clicked.connect(self.clicked_mask_mode)
        self.pushButton_light_setting.clicked.connect(self.clicked_light_setting)
        self.pushButton_auto_adjust_n1.clicked.connect(
            partial(self.clicked_auto_adjust_noise, mode="EQUAL")
        )
        self.pushButton_auto_adjust_n1_plus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, mode="UP")
        )
        self.pushButton_auto_adjust_n1_minus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, mode="DOWN")
        )
        self.pushButton_terminate.clicked.connect(self.clicked_terminate)

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
            self.actionTelnet_Settings.setEnabled(True)  # type: ignore
            self.actionFTP_Settings.setEnabled(True)  # type: ignore
            self.actionLocal_File_Path.setEnabled(True)  # type: ignore
            self.actionEdit_target_tolerance.setEnabled(True)  # type: ignore
            self.actionEdit_Saturation_Target_mV.setEnabled(True)  # type: ignore
            self.actionEdit_Oversaturate_Threshold.setEnabled(True)  # type: ignore
            self.actionEdit_Line_Number.setEnabled(True)  # type: ignore
        else:
            message = QMessageBox()
            message.setWindowTitle("Error")
            message.setText("Invalid Username or Password")
            message.setIcon(QMessageBox.Critical)
            message.exec()

    def open_telnet_settings_dialog(self):
        # Create a new TelnetSettingsDialog
        dialog = TelnetSettingsDialog(self.app_config)
        logging.debug("Telnet settings dialog created")
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
        logging.debug("FTP settings dialog created")
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
            self.app_config.save_config_to_file()

    def open_target_tolerance_dialog(self):
        # let the user select a target tolerance and write back to the config file
        target_tolerance, ok = QInputDialog.getDouble(
            self, "Target Tolerance", "Enter Target Tolerance", 0.01, 0.0, 100.0, 3
        )
        if ok:
            self.app_config.set_target_tolerance(target_tolerance)
            self.app_config.save_config_to_file()

    def open_saturation_target_dialog(self):
        # let the user select a saturation target and write back to the config file
        saturation_target, ok = QInputDialog.getDouble(
            self, "Saturation Target", "Enter Saturation Target", 769.0, 0.0, 770.0, 1
        )
        if ok:
            self.app_config.set_target_saturation(saturation_target)
            self.app_config.save_config_to_file()

    def open_oversaturate_threshold_dialog(self):
        description = "This is the number of pixels to check whether the image is flat or not, determine its saturation status."
        QMessageBox.information(self, "Oversaturated Threshold", description)
        oversaturated_threshold, ok = QInputDialog.getDouble(
            self,
            "Oversaturated Threshold",
            "Enter Oversaturated Threshold",
            20.0,
            10.0,
            100.0,
            1,
        )
        if ok:
            self.app_config.set_flatness_check_threshold(oversaturated_threshold)
            self.app_config.save_config_to_file()

    def open_line_number_dialog(self):
        # let the user select a line number and write back to the config file
        # range from 0 to 32767
        line_number, ok = QInputDialog.getInt(
            self, "Line Number", "Enter Line Number", 580, 0, 32767, 1
        )
        if ok:
            self.app_config.set_line_number(line_number)
            self.app_config.save_config_to_file()
            # prompt the user to press initialize LV5600
            message = QMessageBox()
            message.setWindowTitle("Info")
            message.setText("Please press Initialize LV5600")
            message.setIcon(QMessageBox.Information)
            message.exec()

    def show_about_dialog(self):
        # Create a new AboutDialog
        dialog = AboutDialog()
        logging.debug("About dialog created")
        # Show the dialog modally
        dialog.exec()

    @asyncSlot()
    async def establish_connection(self):
        try:
            status = await ConnectionTask.connect_to_telnet(self.telnet_client)
            if status == True:
                logging.info("Telnet connection established")
            else:
                logging.error("Telnet connection failed")
        except Exception as e:
            logging.error("Error establishing Telnet connection: " + str(e))
            await self.telnet_client.close()
            self.dialog_handler.show_error_dialog("Check if the LV5600 is connected!")
            return

        try:
            status = ConnectionTask.connect_to_debugconsole(
                self.debug_console_controller
            )
            if status == True:
                logging.info("Debug console connection established")
            else:
                logging.error("Debug console connection failed")
        except Exception as e:
            self.dialog_handler.show_error_dialog(
                "Check if the debug console is connected!"
            )
            logging.error("Error establishing Debug console connection: " + str(e))
            return

        # disable establish connection related components
        self.pushButton_establish_connection.setEnabled(False)

        # enable other components
        self.pushButton_initialize_lv5600.setEnabled(True)
        self.pushButton_auto_wb.setEnabled(True)
        self.pushButton_capture_n_classify_sat.setEnabled(True)
        self.pushButton_auto_adjust_sat.setEnabled(True)
        self.pushButton_SAT_mode.setEnabled(True)
        self.pushButton_mask_mode.setEnabled(True)
        self.pushButton_light_setting.setEnabled(True)
        self.pushButton_capture_n_send_bmp.setEnabled(True)
        self.pushButton_auto_adjust_n1.setEnabled(True)
        self.pushButton_auto_adjust_n1_plus20.setEnabled(True)
        self.pushButton_auto_adjust_n1_minus20.setEnabled(True)
        self.pushButton_terminate.setEnabled(True)
        self.textBrowser.setEnabled(True)
        self.graphicsView.setEnabled(True)
        self.label_graphics.setEnabled(True)
        self.label_n1.setEnabled(True)
        self.label_n1plus20.setEnabled(True)
        self.label_n1minus20.setEnabled(True)
        self.label_SAT_mode.setEnabled(True)
        self.label_mask_mode.setEnabled(True)
        self.lcdNumber_n1.setEnabled(True)
        self.lcdNumber_n1plus20.setEnabled(True)
        self.lcdNumber_n1minus20.setEnabled(True)
        self.progressBar.setEnabled(True)
        self.pushButton_capture_sat_value.setEnabled(True)

        # check whether local directory exists
        local_dir = self.app_config.get_local_file_path()
        if not os.path.exists(local_dir):
            # create the local directory
            os.makedirs(local_dir)

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

        try:
            await LV5600Tasks.initialize_lv5600(self.telnet_client)
            logging.info("-------------------- LV5600 initialized --------------------")
        except Exception as e:
            logging.error("Error initializing LV5600: " + str(e))
            self.dialog_handler.show_error_dialog("Error initializing LV5600!")
            return

    @asyncSlot()
    async def clicked_capture_n_send_bmp(self, mode="SAT", message=None):
        logging.info(
            "-------------------- Capturing and sending BMP --------------------"
        )
        exec_status = False
        self.progressBar.setValue(0)
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )

        try:
            with FTPSession(self.ftp_client) as ftp_client:
                exec_status = await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                mv = self.waveform_image_analysis_controller.get_current_mv(
                    local_file_path,
                    CalculationConstants.SAT_MODE,
                    CalculationConstants.ROI_COORDINATES_X1,
                    CalculationConstants.ROI_COORDINATES_X2,
                    CalculationConstants.ROI_COORDINATES_Y1,
                    CalculationConstants.ROI_COORDINATES_Y2,
                )
                # display in graphics view
                pixmap = QPixmap(local_file_path)
                if message == None:
                    self.display_image_and_title(pixmap, "Current mV: " + str(mv))
                else:
                    self.display_image_and_title(pixmap, message)
                self.progressBar.setValue(100)

                if exec_status:
                    self.progressBar.setValue(100)
                    logging.info(
                        "-------------------- BMP captured and sent --------------------"
                    )
        except Exception as e:
            logging.error("Error capturing and sending BMP: " + str(e))
            self.dialog_handler.show_error_dialog("Error capturing and sending BMP!")
            return

        if not exec_status:
            logging.error("BMP capture and send failed")
            return

    @asyncSlot()
    async def clicked_capture_sat_value(self):
        self.debug_console_controller.activate()
        self.debug_console_controller.set_light_level(200)
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        with FTPSession(self.ftp_client) as ftp_client:
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, local_file_path
            )
            mv = self.waveform_image_analysis_controller.get_current_mv(
                local_file_path,
                CalculationConstants.SAT_MODE,
                CalculationConstants.ROI_COORDINATES_X1,
                CalculationConstants.ROI_COORDINATES_X2,
                CalculationConstants.ROI_COORDINATES_Y1,
                CalculationConstants.ROI_COORDINATES_Y2,
            )
            cursor = mv / CalculationConstants.CURSOR_TO_MV_FACTOR
            self.app_config.set_target_saturation(mv)
            self.app_config.save_config_to_file()
            # put the cursor on the target saturation
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)
            # display in graphics view
            pixmap = QPixmap(local_file_path)
            self.display_image_and_title(pixmap, "Target Saturation mV: " + str(mv))
            logging.info(f"Target saturation set to {mv} mV")

    @asyncSlot()
    async def clicked_capture_n_classify(self, mode="SAT", message=None):
        logging.info("Capturing and classifying SAT")
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        sat_target = self.app_config.get_target_saturation()
        class_, mv = await self.average_n_classify_helper(local_file_path, sat_target)

        # capture a new image as result
        with FTPSession(self.ftp_client) as ftp_client:
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, local_file_path
            )
        # display in graphics view
        pixmap = QPixmap(local_file_path)
        if mode == "SAT":
            self.display_image_and_title(pixmap, f"SAT: {class_}")
        elif mode == "NOISE":
            self.display_image_and_title(pixmap, f"Current mV: {mv}")
        else:
            self.display_image_and_title(pixmap, message)
        logging.info("SAT captured and classified")

    @asyncSlot()
    async def average_n_classify_helper(
        self,
        local_file_path,
        target,
        mode="SAT",
        progressBarOn=True,
    ):
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)

            # capture multiple images and preprocess them to get the mean mid_cyan_y_value
            mv_values = []
            self.progressBar.setValue(0) if progressBarOn else None
            for i in range(CalculationConstants.AVERAGE_COUNT):
                logging.info(f"Processing image {i+1}")
                await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                pixmap = QPixmap(local_file_path)
                self.display_image_and_title(pixmap, "Processing image " + str(i + 1))
                mv_value = self.waveform_image_analysis_controller.get_current_mv(
                    local_file_path,
                    CalculationConstants.SAT_MODE,
                    CalculationConstants.ROI_COORDINATES_X1,
                    CalculationConstants.ROI_COORDINATES_X2,
                    CalculationConstants.ROI_COORDINATES_Y1,
                    CalculationConstants.ROI_COORDINATES_Y2,
                )
                mv_values.append(mv_value)
                self.progressBar.setValue(
                    int((i + 1) * 100 / CalculationConstants.AVERAGE_COUNT)
                ) if progressBarOn else None

            # Get the mean mv_value
            mv = sum(mv_values) / len(mv_values)
            cursor = mv / CalculationConstants.CURSOR_TO_MV_FACTOR
            mv = round(mv, 1)
            cursor = round(cursor)
            logging.debug(f"Cursor: {cursor}, MV: {mv}")

            flatness_pixelCount = self.app_config.get_flatness_check_pixel()
            flatness_sv_threshold = self.app_config.get_flatness_check_sv_threshold()

            logging.info(
                "Flatness params: "
                + str(flatness_pixelCount)
                + ""
                + str(flatness_sv_threshold)
            )
            # classify SAT using mv
            tolerance = self.app_config.get_target_tolerance()
            class_ = self.waveform_image_analysis_controller.classify_waveform(
                local_file_path,
                target,
                tolerance,
                flatness_pixelCount,
                flatness_sv_threshold,
                CalculationConstants.ROI_COORDINATES_X1,
                CalculationConstants.ROI_COORDINATES_X2,
                CalculationConstants.ROI_COORDINATES_Y1,
                CalculationConstants.ROI_COORDINATES_Y2,
                CalculationConstants.SAT_MODE,
            )
            logging.info("DLL Classification Result:" + str(class_))
            if mode == "SAT":
                if class_ == 0:
                    class_ = "Over Saturated"
                elif class_ == 1:
                    class_ = "Under Saturated"
                elif class_ == 2:
                    class_ = "Just Saturated"
                else:
                    logging.error("Classification Result is:" + str(class_))
                    class_ = "Unknown"
            elif mode == "NOISE":
                if class_ == 0:
                    class_ = "high"
                elif class_ == 1:
                    class_ = "low"
                elif class_ == 2:
                    class_ = "pass"
                else:
                    logging.error("Classification Result is:" + str(class_))
                    class_ = "Unknown"

            # turn on scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

            return class_, mv

    @asyncSlot()
    async def clicked_auto_wb(self):
        logging.info("-------------------- Capturing N1 Value --------------------")
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)
            self.progressBar.setValue(0)
            # capture multiple images and preprocess them to get the mean mid_cyan_y_value
            mv_values = []
            for i in range(CalculationConstants.AVERAGE_COUNT):
                logging.info(f"Processing image {i+1}")
                # capture an image
                await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                pixmap = QPixmap(local_file_path)
                self.display_image_and_title(pixmap, "Processing image " + str(i + 1))
                mv_value = self.waveform_image_analysis_controller.get_current_mv(
                    local_file_path,
                    CalculationConstants.NOISE_MODE,
                    CalculationConstants.ROI_COORDINATES_X1,
                    CalculationConstants.ROI_COORDINATES_X2,
                    CalculationConstants.ROI_COORDINATES_Y1,
                    CalculationConstants.ROI_COORDINATES_Y2,
                )
                mv_values.append(mv_value)
                self.progressBar.setValue(
                    int((i + 1) * 100 / CalculationConstants.AVERAGE_COUNT)
                )

            # get cursor and mv
            mv = sum(mv_values) / len(mv_values)
            cursor = mv / CalculationConstants.CURSOR_TO_MV_FACTOR
            logging.debug(f"Cursor: {cursor}, MV: {mv}")

            # turn on scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

            # capture a new image as result
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, local_file_path
            )
            # display in graphics view
            pixmap = QPixmap(local_file_path)
            self.display_image_and_title(pixmap, f"WB n1 value: {mv}")
            self.wb_n1_value = mv
            self.lcdNumber_n1.display(self.wb_n1_value)
            self.lcdNumber_n1plus20.display(self.wb_n1_value + 20)
            self.lcdNumber_n1minus20.display(self.wb_n1_value - 20)

        logging.info(
            "-------------------- N1 Value captured --------------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_sat(self):
        self.debug_console_controller.set_mask_mode("ON")
        self.label_mask_mode.setText("Mask On")
        sleep(2)
        self.debug_console_controller.reset_light_level()
        logging.info("-------------------- Auto Adjust Saturation --------------------")
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        light_level = 0
        mv_queue = []
        light_level_queue = []
        queue_size = 3
        target = self.app_config.get_target_saturation()
        self.progressBar.setValue(0)
        while True:
            class_, mv = await self.average_n_classify_helper(
                local_file_path, target=target, progressBarOn=False
            )

            logging.info(f"Class: {class_}, MV: {mv}")
            logging.info(f"Current Light Level: {light_level}")

            # append new light_level and mv values to queue and maintain its size
            light_level_queue.append(light_level)
            mv_queue.append(mv)

            if len(light_level_queue) > queue_size and len(mv_queue) > queue_size:
                light_level_queue.pop(0)
                mv_queue.pop(0)

            if (
                len(set(light_level_queue)) == 2
                and len(light_level_queue) > 2
                and class_ != "Just Saturated"
            ):
                logging.warning("Oscillation detected. Please adjust manually.")
                await LV5600Tasks.scale_and_cursor(
                    self.telnet_client,
                    True,
                    target / CalculationConstants.CURSOR_TO_MV_FACTOR,
                )
                while True:
                    message = QMessageBox()
                    message.setIcon(QMessageBox.Warning)
                    if class_ == "Under Saturated":
                        message.setText(
                            "Waveform is under saturated. Move the Scope Digital-End nearer to Chart Surface"
                        )
                    elif class_ == "Over Saturated":
                        message.setText(
                            "Waveform is over saturated. Move the Scope Digital-End further from Chart Surface"
                        )
                    message.setWindowTitle("Warning")
                    message.setInformativeText("Press OK to continue")
                    message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    message.setDefaultButton(QMessageBox.Ok)
                    ret = message.exec_()
                    if ret == QMessageBox.Ok:
                        break
                    if ret == QMessageBox.Cancel:
                        logging.info("User cancelled, go back to main menu")
                        return
                continue

            # if we have enough data points, perform linear regression
            if (
                len(mv_queue) >= queue_size
                and mv < target * CalculationConstants.JUMP_THRESHOLD
            ):
                x = np.array(light_level_queue)
                y = np.array(mv_queue)
                coefficients = np.polyfit(x, y, 1)
                slope = coefficients[0]
                intercept = coefficients[1]

                # predict the light level that would give an mv value close to the target
                predicted_light_level = (
                    target * CalculationConstants.JUMP_THRESHOLD - intercept
                ) / slope
                predicted_light_level = int(
                    round(min(max(predicted_light_level, 0), 255))
                )  # ensure predicted_light_level is within 0-255, prevent overflow

                # ensure prediced_light_level is smaller than current light level + 20 (prevent overstepping)
                if predicted_light_level > light_level + 20:
                    predicted_light_level = light_level + 20

                if predicted_light_level <= light_level:
                    predicted_light_level = light_level + 1
                # adjust the light level towards the predicted_light_level
                logging.info(f"Predicted Light Level: {predicted_light_level}")
                self.debug_console_controller.tune_to_target_level(
                    predicted_light_level, light_level
                )
                light_level = predicted_light_level

            elif mv < target * CalculationConstants.JUMP_THRESHOLD:
                logging.info("mv is below threshold, tuning up light")
                self.debug_console_controller.tune_up_light()
                light_level += 1
            else:
                if class_ == "Under Saturated":
                    logging.info("Single stepping up")
                    self.debug_console_controller.tune_up_light()
                    light_level += 1
                elif class_ == "Over Saturated":
                    logging.info("Single stepping down")
                    self.debug_console_controller.tune_down_light()
                    light_level -= 1
                elif class_ == "Just Saturated":
                    break
                else:
                    logging.error("Invalid class")
                    break
            # use current mv and target mv to calculate progress
            progress = int(round((1 - abs(target - mv) / abs(target - 0)) * 100))

            self.progressBar.setValue(progress)

        self.progressBar.setValue(100)
        await self.clicked_capture_n_send_bmp(mode="SAT", message=f"Final mV: {mv}")
        logging.info(
            "-------------------- Auto Adjust Saturation Done --------------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_noise(self, mode):
        self.debug_console_controller.set_mask_mode("ON")
        self.label_mask_mode.setText("Mask On")
        sleep(2)
        if mode not in ["UP", "DOWN", "EQUAL"]:
            logging.warning("Invalid mode!")
            message = QMessageBox()
            message.setIcon(QMessageBox.Warning)
            message.setText("Invalid mode!")
            message.setWindowTitle("Warning")
            message.exec_()
            return
        if self.wb_n1_value == -1:
            logging.warning("Please perform Auto WB first!")
            message = QMessageBox()
            message.setIcon(QMessageBox.Warning)
            message.setText("Please perform Auto WB first!")
            message.setWindowTitle("Warning")
            message.exec_()
            return
        else:
            logging.info("-------------------- Auto Adjust Noise --------------------")
            if mode == "UP":
                target = self.wb_n1_value + 20
            elif mode == "DOWN":
                target = self.wb_n1_value - 20
            elif mode == "EQUAL":
                target = self.wb_n1_value
            else:
                return

            self.debug_console_controller.reset_light_level()
            local_file_path = os.path.join(
                self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
            )
            light_level, mv_queue, light_level_queue, queue_size = 0, [], [], 3

            while True:
                class_, mv = await self.average_n_classify_helper(
                    local_file_path, target=target, mode="NOISE", progressBarOn=False
                )
                logging.info(f"Target mV value: {target}")
                logging.info(f"Class: {class_}, Current MV: {mv}")
                logging.info(f"Current Light Level: {light_level}")

                # append new light_level and mv values to queue and maintain its size
                light_level_queue.append(light_level)
                mv_queue.append(mv)

                if len(light_level_queue) > queue_size and len(mv_queue) > queue_size:
                    light_level_queue.pop(0)
                    mv_queue.pop(0)

                if (
                    len(set(light_level_queue)) == 2
                    and len(light_level_queue) > 2
                    and class_ != "pass"
                ):
                    logging.warning("Oscillation detected. Please adjust manually.")
                    await LV5600Tasks.scale_and_cursor(
                        self.telnet_client,
                        True,
                        target / CalculationConstants.CURSOR_TO_MV_FACTOR,
                    )
                    while True:
                        message = QMessageBox()
                        message.setIcon(QMessageBox.Warning)
                        if class_ == "low":
                            message.setText(
                                "Waveform under target value. Move the Scope Digital-End nearer to Chart Surface"
                            )
                        elif class_ == "high":
                            message.setText(
                                "Waveform over target value. Move the Scope Digital-End further from Chart Surface"
                            )
                        message.setWindowTitle("Warning")
                        message.setInformativeText("Press OK to continue")
                        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                        message.setDefaultButton(QMessageBox.Ok)
                        ret = message.exec_()
                        if ret == QMessageBox.Ok:
                            break
                        if ret == QMessageBox.Cancel:
                            logging.info("User cancelled, go back to main menu")
                            return
                    continue

                # if we have enough data points, perform linear regression
                if (
                    len(mv_queue) >= queue_size
                    and mv < target * CalculationConstants.JUMP_THRESHOLD
                ):
                    x = np.array(light_level_queue)
                    y = np.array(mv_queue)
                    coefficients = np.polyfit(x, y, 1)
                    slope = coefficients[0]
                    intercept = coefficients[1]

                    # predict the light level that would give an mv value close to the target
                    predicted_light_level = (
                        target * CalculationConstants.JUMP_THRESHOLD - intercept
                    ) / slope
                    predicted_light_level = int(
                        round(min(max(predicted_light_level, 0), 255))
                    )

                    # ensure prediced_light_level is smaller than current light level + 20 (prevent overstepping)
                    if predicted_light_level > light_level + 20:
                        predicted_light_level = light_level + 20

                    if predicted_light_level <= light_level:
                        predicted_light_level = light_level + 1

                    # adjust the light level towards the predicted_light_level
                    logging.info(f"Predicted Light Level: {predicted_light_level}")
                    self.debug_console_controller.tune_to_target_level(
                        predicted_light_level, light_level
                    )
                    light_level = predicted_light_level

                elif mv < target * CalculationConstants.JUMP_THRESHOLD:
                    logging.info("mv is below threshold, tuning up light")
                    self.debug_console_controller.tune_up_light()
                    light_level += 1
                else:
                    if class_ == "low":
                        logging.info("Single stepping up")
                        self.debug_console_controller.tune_up_light()
                        light_level += 1
                    elif class_ == "high":
                        logging.info("Single stepping down")
                        self.debug_console_controller.tune_down_light()
                        light_level -= 1
                    elif class_ == "pass":
                        break
                    else:
                        logging.error("Invalid class")
                        break

                progress = int(round((1 - abs(target - mv) / abs(target - 0)) * 100))
                self.progressBar.setValue(progress)

            final_mv_value = mv_queue[-1]
            logging.info(f"Final MV value: {final_mv_value}")
            # update lcd
            if mode == "UP":
                self.lcdNumber_n1plus20.display(final_mv_value)
            elif mode == "DOWN":
                self.lcdNumber_n1minus20.display(final_mv_value)
            elif mode == "EQUAL":
                self.lcdNumber_n1.display(final_mv_value)

            self.progressBar.setValue(100)
            await self.clicked_capture_n_send_bmp(
                mode="NOISE", message=f"Current mV: {final_mv_value}"
            )
            logging.info(
                "-------------------- Auto Adjust Noise Done --------------------"
            )

    def clicked_sat_mode(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Please select the mode")
        msgBox.setWindowTitle("AGC Mode Selection")

        # add buttons
        WLIButton = msgBox.addButton("WLI", QMessageBox.ActionRole)
        NBIButton = msgBox.addButton("NBI", QMessageBox.ActionRole)
        RDIButton = msgBox.addButton("RDI", QMessageBox.ActionRole)
        OnButton = msgBox.addButton("ON", QMessageBox.ActionRole)
        OffButton = msgBox.addButton("OFF", QMessageBox.ActionRole)

        # show message box
        msgBox.exec_()

        # handle button clicks
        if msgBox.clickedButton() == WLIButton:
            logging.info("WLI mode selected")
            self.debug_console_controller.set_AGC_mode("WLI")
            self.label_SAT_mode.setText("WLI")
        elif msgBox.clickedButton() == NBIButton:
            logging.info("NBI mode selected")
            self.debug_console_controller.set_AGC_mode("NBI")
            self.label_SAT_mode.setText("NBI")
        elif msgBox.clickedButton() == RDIButton:
            logging.info("RDI mode selected")
            self.debug_console_controller.set_AGC_mode("RDI")
            self.label_SAT_mode.setText("RDI")
        elif msgBox.clickedButton() == OnButton:
            logging.info("AGC On mode selected")
            self.debug_console_controller.set_AGC_mode("ON")
            self.label_SAT_mode.setText("AGC On")
        elif msgBox.clickedButton() == OffButton:
            logging.info("AGC Off mode selected")
            self.debug_console_controller.set_AGC_mode("OFF")
            self.label_SAT_mode.setText("AGC Off")

        logging.info("-------------------- AGC mode set --------------------")

    def clicked_mask_mode(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Please select the mode")
        msgBox.setWindowTitle("Mask Mode Selection")

        # add buttons
        OnButton = msgBox.addButton("ON", QMessageBox.ActionRole)
        OffButton = msgBox.addButton("OFF", QMessageBox.ActionRole)
        CrossButton = msgBox.addButton("CROSS", QMessageBox.ActionRole)

        # show message box
        msgBox.exec_()
        # handle button clicks
        if msgBox.clickedButton() == OnButton:
            logging.info("Mask On mode selected")
            self.debug_console_controller.set_mask_mode("ON")
            self.label_mask_mode.setText("Mask On")
        elif msgBox.clickedButton() == OffButton:
            logging.info("Mask Off mode selected")
            self.debug_console_controller.set_mask_mode("OFF")
            self.label_mask_mode.setText("Mask Off")
        elif msgBox.clickedButton() == CrossButton:
            logging.info("Mask Cross mode selected")
            self.debug_console_controller.set_mask_mode("CROSS")
            self.label_mask_mode.setText("Mask X")

        sleep(1)
        logging.info("-------------------- Mask mode set --------------------")

    def clicked_light_setting(self):
        # prompt user to enter the number (0 to 256)
        light_level, ok = QInputDialog.getInt(
            self, "Light Setting", "Enter Light Level", 0, 0, 256, 1
        )
        if ok:
            logging.info(f"Setting light level to {light_level}")
            self.debug_console_controller.set_light_level(light_level)
            logging.info("-------------------- Light level set --------------------")

    @asyncSlot()
    async def clicked_terminate(self):
        logging.warning("You have clicked the terminate button")
        # stop every task that is currently running, go back to when the app launched

        await self.telnet_client.close()
        try:
            self.ftp_client.close()
        except ConnectionError:
            pass
        self.debug_console_controller.stop_tasks()

        # reset the state of UI components
        self.pushButton_establish_connection.setEnabled(True)
        self.pushButton_initialize_lv5600.setEnabled(False)
        self.pushButton_auto_wb.setEnabled(False)
        self.pushButton_capture_n_classify_sat.setEnabled(False)
        self.pushButton_auto_adjust_sat.setEnabled(False)
        self.pushButton_SAT_mode.setEnabled(False)
        self.pushButton_mask_mode.setEnabled(False)
        self.pushButton_light_setting.setEnabled(False)
        self.pushButton_capture_n_send_bmp.setEnabled(False)
        self.pushButton_auto_adjust_n1.setEnabled(False)
        self.pushButton_auto_adjust_n1_plus20.setEnabled(False)
        self.pushButton_auto_adjust_n1_minus20.setEnabled(False)
        self.pushButton_terminate.setEnabled(False)
        self.pushButton_capture_sat_value.setEnabled(False)
        self.textBrowser.setEnabled(False)
        self.graphicsView.setEnabled(False)
        self.label_graphics.setEnabled(False)
        self.label_n1.setEnabled(False)
        self.label_n1plus20.setEnabled(False)
        self.label_n1minus20.setEnabled(False)
        self.label_SAT_mode.setEnabled(False)
        self.label_mask_mode.setEnabled(False)
        self.lcdNumber_n1.setEnabled(False)
        self.lcdNumber_n1plus20.setEnabled(False)
        self.lcdNumber_n1minus20.setEnabled(False)
        self.progressBar.setEnabled(False)

        # reset the state of the lcd
        self.lcdNumber_n1.display(0)
        self.lcdNumber_n1plus20.display(0)
        self.lcdNumber_n1minus20.display(0)

        # reset the state of the graphics view
        self.graphicsView.setScene(None)
        self.label_graphics.setText("Image Display")
        self.label_SAT_mode.setText("Unset")
        self.label_mask_mode.setText("Unset")
        self.progressBar.setValue(0)

        # reset internal state
        self.wb_n1_value = -1

        logging.info("-------------------- Terminated --------------------")
