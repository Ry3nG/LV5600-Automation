from functools import partial, partialmethod
import logging
import os
import numpy as np
from time import sleep
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

        # TODO : Bind menu bar actions to functions here

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
        # TODO : Bind button actions to functions here
        self.pushButton_login.clicked.connect(self.login)
        self.pushButton_establish_connection.clicked.connect(self.establish_connection)
        self.pushButton_initialize_lv5600.clicked.connect(
            self.clicked_initialize_lv5600
        )
        self.pushButton_capture_n_send_bmp.clicked.connect(
            self.clicked_capture_n_send_bmp
        )
        self.pushButton_recall_preset.clicked.connect(self.clicked_recall_preset)
        self.pushButton_capture_n_classify_sat.clicked.connect(
            self.clicked_capture_n_classify_sat
        )
        self.pushButton_auto_wb.clicked.connect(self.clicked_auto_wb)
        self.pushButton_auto_adjust_sat.clicked.connect(self.clicked_auto_adjust_sat)
        self.pushButton_auto_adjust_n1_plus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, mode="UP")
        )
        self.pushButton_auto_adjust_n1_minus20.clicked.connect(
            partial(self.clicked_auto_adjust_noise, mode="DOWN")
        )

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
            self.actionTelnet_Settings.setEnabled(True) # type: ignore
            self.actionFTP_Settings.setEnabled(True) # type: ignore
            self.actionLocal_File_Path.setEnabled(True) # type: ignore
            self.actionEdit_target_tolerance.setEnabled(True) # type: ignore
            self.actionEdit_Saturation_Target_mV.setEnabled(True) # type: ignore
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

    @asyncSlot()
    async def establish_connection(self):
        try:
            logging.info("Establishing Telnet connection")
            logging.debug("Telnet address: " + self.app_config.get_telnet_address())
            logging.debug("Telnet port: " + str(self.app_config.get_telnet_port()))
            logging.debug("Telnet username: " + self.app_config.get_telnet_username())
            logging.debug("Telnet password: " + self.app_config.get_telnet_password())
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
        logging.info(
            "-------------------- Capturing and sending BMP --------------------"
        )
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        with FTPSession(self.ftp_client) as ftp_client:
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, local_file_path
            )
            # display in graphics view
            pixmap = QPixmap(local_file_path)
            self.display_image_and_title(pixmap, "Snapshot")
        logging.info("-------------------- BMP captured and sent --------------------")

    @asyncSlot()
    async def clicked_recall_preset(self):
        preset_number, ok = QInputDialog.getInt(
            self, "Recall Preset", "Enter Preset Number (1-60):", 1, 1, 60, 1
        )
        if ok:
            logging.info(
                f"-------------------- Recalling Preset {preset_number} --------------------"
            )
            await LV5600Tasks.recall_preset(self.telnet_client, preset_number)
            logging.info(
                f"-------------------- Preset {preset_number} recalled --------------------"
            )

    @asyncSlot()
    async def average_n_classify_helper(
        self,
        local_file_path,
        target=CalculationConstants.MAX_SATURATION_MV_VALUE,
        mode="SAT",
    ):
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)

            # capture multiple images and preprocess them to get the mean mid_cyan_y_value
            mid_cyan_y_values = []
            for i in range(CalculationConstants.AVERAGE_COUNT):
                logging.info(f"Processing image {i+1}")
                await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                mid_cyan_y_value = await CalculationTasks.preprocess_and_get_mid_cyan(
                    mode
                )
                mid_cyan_y_values.append(mid_cyan_y_value)

            # get the mean mid_cyan_y_value
            mean_cyan_y_value = sum(mid_cyan_y_values) / len(mid_cyan_y_values)
            logging.debug(f"Mean Cyan Y Value: {mean_cyan_y_value}")

            # get cursor and mv
            cursor, mv = CalculationTasks.get_cursor_and_mv(mean_cyan_y_value)
            logging.debug(f"Cursor: {cursor}, MV: {mv}")

            # classify SAT using mv
            tolerance = self.app_config.get_target_tolerance()
            class_ = CalculationTasks.classify_mv_level(mv, target, tolerance)

            if mode == "SAT":
                if class_ == "pass":
                    class_ = "Just Saturated"
                elif class_ == "low":
                    class_ = "Under Saturated"
                elif class_ == "high":
                    class_ = "Over Saturated"

            # turn on scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, True, cursor)

            return class_, mv

    @asyncSlot()
    async def clicked_capture_n_classify_sat(self):
        logging.info("Capturing and classifying SAT")
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        class_, mv = await self.average_n_classify_helper(local_file_path)

        # capture a new image as result
        with FTPSession(self.ftp_client) as ftp_client:
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_client, ftp_client, local_file_path
            )

        # display in graphics view
        pixmap = QPixmap(local_file_path)
        self.display_image_and_title(pixmap, f"SAT: {class_}")
        logging.info("SAT captured and classified")

    @asyncSlot()
    async def clicked_auto_wb(self):
        logging.info("-------------------- Auto White Balance --------------------")
        local_file_path = os.path.join(
            self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
        )
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_client, False)

            # capture multiple images and preprocess them to get the mean mid_cyan_y_value
            mid_cyan_y_values = []
            for i in range(CalculationConstants.AVERAGE_COUNT):
                logging.info(f"Processing image {i+1}")
                # capture an image
                await LV5600Tasks.capture_n_send_bmp(
                    self.telnet_client, ftp_client, local_file_path
                )
                # preprocess the image
                mid_cyan_y_value = await CalculationTasks.preprocess_and_get_mid_cyan(
                    "WB"
                )
                mid_cyan_y_values.append(mid_cyan_y_value)

            # get the mean mid_cyan_y_value
            mean_cyan_y_value = sum(mid_cyan_y_values) / len(mid_cyan_y_values)
            logging.debug(f"Mean Cyan Y Value: {mean_cyan_y_value}")
            # get cursor and mv
            cursor, mv = CalculationTasks.get_cursor_and_mv(mean_cyan_y_value)
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

        logging.info(
            "-------------------- Auto White Balance Done --------------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_sat(self):
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
        while True:
            class_, mv = await self.average_n_classify_helper(local_file_path)
            logging.info(f"Class: {class_}, MV: {mv}")
            logging.info(f"Current Light Level: {light_level}")
            if class_ == "Just Saturated":
                break

            # append new light_level and mv values to queue and maintain its size
            light_level_queue.append(light_level)
            mv_queue.append(mv)

            if len(light_level_queue) > queue_size and len(mv_queue) > queue_size:
                light_level_queue.pop(0)
                mv_queue.pop(0)

            if len(set(light_level_queue)) == 2 and len(light_level_queue) > 2:
                logging.warning("Oscillation detected. Please adjust manually.")
                await LV5600Tasks.scale_and_cursor(
                    self.telnet_client,
                    True,
                    target / CalculationConstants.CURSOR_TO_MV_FACTOR,
                )
                while True:
                    message = QMessageBox()
                    message.setIcon(QMessageBox.Warning)
                    message.setText("Oscillation detected. Please adjust manually.")
                    message.setWindowTitle("Warning")
                    message.setInformativeText("Press OK to continue")
                    message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                    message.setDefaultButton(QMessageBox.Ok)
                    ret = message.exec_()
                    if ret == QMessageBox.Ok:
                        break
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

                # ensure predicted_light_level is greater than current light level
                predicted_light_level = max(predicted_light_level, light_level)
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

        logging.info(
            "-------------------- Auto Adjust Saturation Done --------------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_noise(self, mode):
        if mode not in ["UP", "DOWN"]:
            logging.warning("Invalid mode. Mode must be either 'UP' or 'DOWN'.")
            message = QMessageBox()
            message.setIcon(QMessageBox.Warning)
            message.setText("Invalid mode. Mode must be either 'UP' or 'DOWN'.")
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
            target = self.wb_n1_value + 20 if mode == "UP" else self.wb_n1_value - 20

            self.debug_console_controller.reset_light_level()
            local_file_path = os.path.join(
                self.app_config.get_local_file_path(), FTPConstants.LOCAL_FILE_NAME_BMP
            )
            light_level, mv_queue, light_level_queue, queue_size = 0, [], [], 3
            while True:
                class_, mv = await self.average_n_classify_helper(
                    local_file_path, target=target, mode="NOISE"
                )
                logging.info(f"Target mV value: {target}")
                logging.info(f"Class: {class_}, Current MV: {mv}")
                logging.info(f"Current Light Level: {light_level}")
                if class_ == "pass":
                    break

                # append new light_level and mv values to queue and maintain its size
                light_level_queue.append(light_level)
                mv_queue.append(mv)

                if len(light_level_queue) > queue_size and len(mv_queue) > queue_size:
                    light_level_queue.pop(0)
                    mv_queue.pop(0)

                if len(set(light_level_queue)) == 2 and len(light_level_queue) > 2:
                    logging.warning("Oscillation detected. Please adjust manually.")
                    await LV5600Tasks.scale_and_cursor(
                        self.telnet_client,
                        True,
                        target / CalculationConstants.CURSOR_TO_MV_FACTOR,
                    )
                    while True:
                        message = QMessageBox()
                        message.setIcon(QMessageBox.Warning)
                        message.setText("Oscillation detected. Please adjust manually.")
                        message.setWindowTitle("Warning")
                        message.setInformativeText("Press OK to continue")
                        message.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                        message.setDefaultButton(QMessageBox.Ok)
                        ret = message.exec_()
                        if ret == QMessageBox.Ok:
                            break
                    continue

                if class_ == "low":
                    logging.info("Single stepping up")
                    self.debug_console_controller.tune_up_light()
                    light_level += 1
                elif class_ == "high":
                    logging.info("Single stepping down")
                    self.debug_console_controller.tune_down_light()
                    light_level -= 1

            logging.info(
                "-------------------- Auto Adjust Noise Done --------------------"
            )