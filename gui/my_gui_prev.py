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
            partial(self.clicked_auto_adjust_noise, offset = 0)
        )
        self.pushButton_auto_adjust_n1_plus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, offset = 20)
        )
        self.pushButton_auto_adjust_n1_minus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, offset = -20)
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
    async def clicked_capture_n_send_bmp(self, mode=CalculationConstants.SAT_MODE, message=None):
        logging.info(
            "-------------------- Capturing and sending BMP --------------------"
        )
        exec_status = False
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )

        try:
            with FTPSession(self.ftp_client) as ftp_client:
                exec_status = await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                mv, cursor = self.waveform_image_analysis_controller.compute_mv_cursor(
                    local_file_path, mode
                )
                # display in graphics view
                pixmap = QPixmap(local_file_path)
                if message == None:
                    self.display_image_and_title(pixmap, "Current mV: " + str(mv))
                else:
                    self.display_image_and_title(pixmap, message)

                if exec_status:
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
            mv, cursor = self.waveform_image_analysis_controller.compute_mv_cursor(
                self.getLocalFilePath(), CalculationConstants.SAT_MODE
            )
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
        mv, cursor, sd = await self.compute_average_mv_sd(CalculationConstants.SAT_MODE)
        target = self.app_config.get_target_saturation()
        tolerance = self.app_config.get_target_tolerance()
        flat_sv_threshold = self.app_config.get_flatness_check_sv_threshold()
        class_ = self.waveform_image_analysis_controller.classify_waveform(
            mv,
            sd,
            target,
            tolerance,
            flat_sv_threshold,
            CalculationConstants.SAT_MODE,
        )
        if class_ == 0:
            class_ = "Over Saturated"
        elif class_ == 1:
            class_ = "Under Saturated"
        elif class_ == 2:
            class_ = "Just Saturated"
        else:
            logging.error("Classification Result is:" + str(class_))
            class_ = "Unknown"
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


    def getLocalFilePath(self):
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(),
            FTPConstants.LOCAL_FILE_NAME_BMP,
        )
        return local_file_path
    
    @asyncSlot()
    async def capture_image_to_local(self):
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, self.getLocalFilePath()
            )
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True)

    @asyncSlot()
    async def compute_average_mv_sd(
        self,
        mode,
        num_sample = 3
    ):
        total_mv = 0
        max_sd = 0
        for i in range(num_sample):
            await self.capture_image_to_local()
            self.display_image_and_title(
                QPixmap(self.getLocalFilePath()), f"Processing image {i+1}"
            )
            mv, cursor = self.waveform_image_analysis_controller.compute_mv_cursor(
                self.getLocalFilePath(), mode
            )

            flat_pixel_count = self.app_config.get_flatness_check_pixel()
            sd = self.waveform_image_analysis_controller.get_current_stdev(
                self.getLocalFilePath(),
                flat_pixel_count,
                CalculationConstants.ROI_COORDINATES_X1,
                CalculationConstants.ROI_COORDINATES_X2,
                CalculationConstants.ROI_COORDINATES_Y1,
                CalculationConstants.ROI_COORDINATES_Y2,
                mode,
            )

            total_mv += mv
            if sd > max_sd:
                max_sd = sd

        res_mv = round(total_mv / num_sample, 1)
        res_sd = max_sd
        res_cursor = res_mv / CalculationConstants.CURSOR_TO_MV_FACTOR

        logging.info(f"Average mV Value for current waveform: {res_mv} mV")
        logging.info(f"Maximum Standard Deviation of mid pixels: {res_sd} ")

        return res_mv, res_cursor, res_sd

    @asyncSlot()
    async def clicked_auto_wb(self):
        logging.info("-------------------- Capturing N1 Value --------------------")
        mv, cursor, sd = await self.compute_average_mv_sd(
            CalculationConstants.NOISE_MODE
        )

        self.app_config.set_target_noise(mv)
        self.app_config.save_config_to_file()

        # Put the cursor on the waveform
        await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

        # display the image on the GUI
        self.display_image_and_title(
            QPixmap(self.getLocalFilePath()), "Current mV: " + str(mv)
        )

        logging.info(f"N1 Value: {mv} mV")
        self.lcdNumber_n1.display(mv)
        self.lcdNumber_n1plus20.display(mv + 20)
        self.lcdNumber_n1minus20.display(mv - 20)

        logging.info("-------------------- N1 Value captured --------------------")

    @asyncSlot()
    async def clicked_auto_adjust_sat(self):
        await self.clicked_capture_sat_value()
        logging.info("-------------------- Auto Adjust Saturation --------------------")
        final_mv = 0

        light_level_upper_bound = 256
        light_level_lower_bound = 0
        checked_light_levels = set()

        target = self.app_config.get_target_saturation()
        tolerance = self.app_config.get_target_tolerance()
        flat_sv_threshold = self.app_config.get_flatness_check_sv_threshold()

        while light_level_lower_bound < light_level_upper_bound:
            middle_light_level = (
                light_level_upper_bound + light_level_lower_bound
            ) // 2

            if middle_light_level in checked_light_levels:
                logging.info("Oscillation detected")
                logging.info(
                    f"Light Level {middle_light_level} has been checked before"
                )
                logging.info("Handing over to precision mode")
                final_mv = await self.adjust_light_level_precisely(
                    CalculationConstants.SAT_MODE, middle_light_level, target
                )
                break

            self.debug_console_controller.set_light_level(middle_light_level)
            sleep(0.2)
            logging.info(f"Current Light Level: {middle_light_level}")

            # Using average mv computation when the difference is less than or equal to 4
            if light_level_upper_bound - light_level_lower_bound <= 8:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.SAT_MODE
                )
            else:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.SAT_MODE, 1
                )
                self.display_image_and_title(
                    QPixmap(self.getLocalFilePath()), "Current mV:"+str(mv)
                )
                

            final_mv = mv
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)
            class_ = self.waveform_image_analysis_controller.classify_waveform(
                mv,
                sd,
                target,
                tolerance,
                flat_sv_threshold,
                CalculationConstants.SAT_MODE,
            )

            checked_light_levels.add(middle_light_level)
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

            if class_ == 0:  # over saturated
                light_level_upper_bound = middle_light_level
            elif class_ == 1:
                light_level_lower_bound = middle_light_level
            elif class_ == 2:
                await self.capture_image_to_local()
                self.display_image_and_title(
                    QPixmap(self.getLocalFilePath()), "Just Saturated"
                )
                break

        await LV5600Tasks.scale_and_cursor(
            self.telnet_client,
            True,
            final_mv / CalculationConstants.CURSOR_TO_MV_FACTOR,
        )
        await LV5600Tasks.capture_n_send_bmp(
            self.telnet_client, self.ftp_client, self.getLocalFilePath()
        )
        self.display_image_and_title(
                    QPixmap(self.getLocalFilePath()), "Just Saturated"
                )
        logging.info(
            "-------------------- Auto Adjust Saturation Done --------------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_noise(self, offset):
        logging.info("-------------------- Setting Noise Value --------------------")

        light_level_upper_bound = 256
        light_level_lower_bound = 0
        checked_light_levels = set()

        target = self.app_config.get_target_noise() + offset
        tolerance = self.app_config.get_target_tolerance()
        flat_sv_threshold = self.app_config.get_flatness_check_sv_threshold()

        final_mv = 0
        while light_level_lower_bound < light_level_upper_bound:
            middle_light_level = (
                light_level_upper_bound + light_level_lower_bound
            ) // 2

            if middle_light_level in checked_light_levels:
                logging.info("Oscillation detected")
                logging.info(
                    f"Light Level {middle_light_level} has been checked before"
                )
                logging.info("Handing over to precision mode")
                final_mv = await self.adjust_light_level_precisely(
                    CalculationConstants.NOISE_MODE, middle_light_level, target
                )

                break

            self.debug_console_controller.set_light_level(middle_light_level)
            sleep(0.2)
            logging.info(f"Current Light Level: {middle_light_level}")

            if light_level_upper_bound - light_level_lower_bound <= 8:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE
                )
            else:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE, 1
                )
                self.display_image_and_title(
                    QPixmap(self.getLocalFilePath()), "Current mV: "+ str(mv)
                )
                

            final_mv = mv
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)
            class_ = self.waveform_image_analysis_controller.classify_waveform(
                mv,
                sd,
                target,
                tolerance,
                flat_sv_threshold,
                CalculationConstants.NOISE_MODE,
            )

            checked_light_levels.add(middle_light_level)
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

            if class_ == 0:
                light_level_upper_bound = middle_light_level
            elif class_ == 1:
                light_level_lower_bound = middle_light_level
            elif class_ == 2:
                
                self.display_image_and_title(
                    QPixmap(self.getLocalFilePath()), "Noise Value Set"
                )
                break

        if offset > 0:
            self.lcdNumber_n1plus20.display(final_mv)
        elif offset < 0:
            self.lcdNumber_n1minus20.display(final_mv)
        else:
            self.lcdNumber_n1.display(final_mv)

        await LV5600Tasks.scale_and_cursor(
            self.telnet_client,
            True,
            final_mv / CalculationConstants.CURSOR_TO_MV_FACTOR,
        )
        await LV5600Tasks.capture_n_send_bmp(
            self.telnet_client, self.ftp_client, self.getLocalFilePath()
        )
        self.display_image_and_title(
            QPixmap(self.getLocalFilePath()), "Current mV: " + str(final_mv)
        )
        logging.info("-------------------- Noise Value Set --------------------")



    @asyncSlot()
    async def adjust_light_level_precisely(self, mode, current_light_level, target):
        logging.debug("Adjusting light level precisely")
        logging.debug("Target: " + str(target) + " mV")
        logging.debug("Current Light Level: " + str(current_light_level))

        checked_light_levels = set()
        differences = {}

        tolerance = self.app_config.get_target_tolerance()
        flat_pixel_count = self.app_config.get_flatness_check_pixel()
        flat_sv_threshold = self.app_config.get_flatness_check_sv_threshold()

        final_mv = 0

        while True:
            self.debug_console_controller.set_light_level(current_light_level)

            # use averaging
            mv, cursor, sd = await self.compute_average_mv_sd(mode)
            difference_from_target = mv - target
            differences[current_light_level] = difference_from_target
            final_mv = mv

            # if the current light level has been checked before
            if current_light_level in checked_light_levels:
                logging.info("Oscillation detected")
                logging.info(
                    f"Light Level {current_light_level} has been checked before"
                )
                # find the closest level to the target, should be absulute value
                closest_level = min(
                    differences.keys(), key=lambda x: abs(differences[x])
                )
                logging.info(f"Closest level: {closest_level}")
                logging.info(f"Closest mV difference: {differences[closest_level]}")

                current_light_level = closest_level
                self.debug_console_controller.set_light_level(current_light_level)

                # message for dialog box to whether increase or decrease the target distance
                # need to check the difference is positive or negative
                if differences[closest_level] < 0:
                    message = f"Current light level is too low. The closest level is {closest_level}. The difference is {round(differences[closest_level],2)} mV. Move the scope closer to the target?"
                    # turn on scale and cursor
                else:
                    message = f"Current light level is too high. The closest level is {closest_level}. The difference is {round(differences[closest_level],2)} mV. Move the scope further away from the target?"

                await LV5600Tasks.scale_and_cursor(
                    self.telnet_client,
                    True,
                    target / CalculationConstants.CURSOR_TO_MV_FACTOR,
                )
                # pop-up
                reply = QMessageBox.question(
                    self,
                    "Message",
                    message,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    checked_light_levels.clear()
                    differences.clear()
                    continue
                else:
                    logging.info("User has chosen to stop the process")
                    break

            class_ = self.waveform_image_analysis_controller.classify_waveform(
                mv, sd, target, tolerance, flat_sv_threshold, mode
            )

            # add the current light level to the checked set
            checked_light_levels.add(current_light_level)

            if class_ == 0:
                current_light_level -= 1
                logging.info(f"Current Light Level: {current_light_level}")
            elif class_ == 1:
                current_light_level += 1
                logging.info(f"Current Light Level: {current_light_level}")
            elif class_ == 2:
                logging.info("Target has reached, returning to previous handler")
                return final_mv


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

        # reset the state of the lcd
        self.lcdNumber_n1.display(0)
        self.lcdNumber_n1plus20.display(0)
        self.lcdNumber_n1minus20.display(0)

        # reset the state of the graphics view
        self.graphicsView.setScene(None)
        self.label_graphics.setText("Image Display")
        self.label_SAT_mode.setText("Unset")
        self.label_mask_mode.setText("Unset")

        # reset internal state
        self.wb_n1_value = -1

        logging.info("-------------------- Terminated --------------------")
