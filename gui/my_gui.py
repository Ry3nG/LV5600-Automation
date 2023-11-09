from functools import partial
import logging
import os
import time
from PyQt5.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFileDialog,
    QInputDialog,
)


from PyQt5 import QtCore, uic
from PyQt5.QtGui import QPixmap
from qasync import asyncSlot
from Constants import CalculationConstants, FTPConstants
from config.application_config import AppConfig
from controllers.debug_console_controller import DebugConsoleController
from controllers.ftp_controller import FTPController
from controllers.ftp_session_controller import FTPSession
from controllers.telnet_controller import TelnetController
from controllers.waveform_image_analysis_controller import (
    WaveformImageAnalysisController,
)
from gui.about_dialog import AboutDialog
from gui.ftp_settings_dialog import FTPSettingsDialog
from gui.log_handler import LogHandler
from gui.resources import resources_rc
import sys
from gui.target_tolerance_dialog import TargetToleranceDialog
from gui.telnet_settings_dialog import TelnetSettingsDialog

from tasks.connection_tasks import ConnectionTask
from tasks.lv5600_tasks import LV5600Tasks
from utils.decorators import time_it_async, time_it_sync


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

    def getLocalFilePath(self):
        local_file_path = os.path.join(
            self.app_config_handler.get_local_file_path(),
            FTPConstants.LOCAL_FILE_NAME_BMP,
        )
        return local_file_path

    def setupUI(self):
        self.loadUIFile("LV5600-Automation-OCB-GUI-2.0.ui")
        # set title
        self.setWindowTitle(
            "LV5600-OCB-Automation-tool"
            + " V"
            + str(self.app_config_handler.get_version())
        )
        self.setupToolBoxView()
        self.setupWelcomeImage()
        self.updateCurrentSettings()
        self.lcdNumber_sat_target_value.display(
            self.app_config_handler.get_target_saturation()
        )

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

        
        self.wfm_image_analysis_controller = WaveformImageAnalysisController()

        self.debug_console_controller = DebugConsoleController()


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

    def display_image(self, local_file_path):
        pixmap = QPixmap(local_file_path)
        new_size = self.graphicsView.size()
        pixmap = pixmap.scaled(new_size, QtCore.Qt.KeepAspectRatio)

        scene = QGraphicsScene()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)
        self.graphicsView.setScene(scene)
        self.graphicsView.fitInView(pixmap_item)

    def setupEvents(self):
        # about
        self.actionAbout.triggered.connect(self.show_about_dialog)
        # Terminate button
        self.pushButton_terminate.clicked.connect(self.terminate)

        # Page 1 - Setup and Initialization
        self.pushButton_establish_connection.clicked.connect(self.establishConnection)
        self.pushButton_initialize_lv5600.clicked.connect(self.initializeLV5600)

        self.pushButton_edit_telnet_settings.clicked.connect(self.editTelnetSettings)
        self.pushButton_edit_ftp_settings.clicked.connect(self.editFTPSettings)
        self.pushButton_edit_local_file_path.clicked.connect(self.editLocalFilePath)
        self.pushButton_edit_target_tolerance.clicked.connect(self.editTargetTolerance)
        self.pushButton_edit_line_number.clicked.connect(self.editLineNumber)

        self.app_config_handler.settings_changed.connect(self.updateCurrentSettings)
        self.pushButton_load_default_settings.clicked.connect(
            self.app_config_handler.set_default_settings
        )

        # Page 2 - OCB Control
        self.pushButton_deliver_mask_mode.clicked.connect(self.deliverMaskMode)
        self.pushButton_deliver_agc_setting.clicked.connect(self.deliverAgcSetting)
        self.pushButton_deliver_light_level.clicked.connect(self.deliverLightLevel)

        # Page 3 - Dynamic Range Automation
        # self.pushButton_capture_sat_value.clicked.connect(self.captureSatValue)
        self.pushButton_classify_sat.clicked.connect(self.classifySat)
        self.pushButton_set_sat.clicked.connect(self.setSat)

        # Page 4 - Noise Automation
        self.pushButton_capturen1.clicked.connect(self.captureN1)
        self.pushButton_setn1.clicked.connect(partial(self.setNoiseValue, 0))
        self.pushButton_setn1p20.clicked.connect(partial(self.setNoiseValue, 20))
        self.pushButton_setn1m20.clicked.connect(partial(self.setNoiseValue, -20))

    def updateCurrentSettings(self):
        current_settings = self.app_config_handler.get_current_settings()
        self.textBrowser_current_settings.setText(current_settings)

    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec_()

    @asyncSlot()
    async def terminate(self):
        logging.warning("You have clicked the terminate button")
        await self.telnet_clinet.close()
        try:
            self.ftp_client.close()
        except Exception as e:
            logging.error(f"Error while closing FTP connection: {str(e)}")

        self.debug_console_controller.stop_tasks()
        self.label_establish_connection.setText(
            "Telnet Disconnected at: " + time.strftime("%H:%M:%S", time.localtime())
        )

    @asyncSlot()
    @time_it_async
    async def establishConnection(self):
        logging.info(
            "-------------------- Establishing Connection --------------------"
        )

        try:
            await ConnectionTask.connect_to_telnet(self.telnet_clinet)
        except Exception as e:
            logging.error(f"Error while establishing connection: {str(e)}")
            return

        self.label_establish_connection.setText(
            "Telnet Connected at: " + time.strftime("%H:%M:%S", time.localtime())
        )
        logging.info("-------------------- Connection Established --------------------")

    @asyncSlot()
    @time_it_async
    async def initializeLV5600(self):
        logging.info("-------------------- Initializing LV5600 --------------------")
        try:
            await LV5600Tasks.initialize_lv5600(self.telnet_clinet)
        except Exception as e:
            logging.error(f"Error while initializing LV5600: {str(e)}")
            return

        self.label_initialize_lv5600.setText(
            "LV5600 Initialized at: " + time.strftime("%H:%M:%S", time.localtime())
        )
        logging.info("-------------------- LV5600 Initialized --------------------")

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
        self.target_tolerance_dialog = TargetToleranceDialog(self.app_config_handler)
        self.target_tolerance_dialog.exec_()

    @asyncSlot()
    async def editLineNumber(self):
        current_value = self.app_config_handler.get_line_number()
        current_value = int(current_value)
        line_number, ok = QInputDialog.getInt(
            self, "Line Number", "Enter Line Number:", current_value, 1, 10000, 1
        )
        if ok:
            self.app_config_handler.set_line_number(line_number)
            self.app_config_handler.save_config_to_file()
            await self.telnet_client.send_command(line_number)

    @time_it_sync
    def deliverMaskMode(self, _=None):
        selected_mode = self.comboBox_mask_mode.currentText()
        logging.info(f"Selected Mask Mode: {selected_mode}")
        if selected_mode == "Mask On":
            self.debug_console_controller.set_mask_mode("ON")
        elif selected_mode == "Mask Off":
            self.debug_console_controller.set_mask_mode("OFF")
        elif selected_mode == "Mask Cross":
            self.debug_console_controller.set_mask_mode("CROSS")

    @time_it_sync
    def deliverAgcSetting(self, _=None):
        selected_setting = self.comboBox_agc_setting.currentText()
        logging.info(f"Selected AGC Setting: {selected_setting}")
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

    @time_it_sync
    def deliverLightLevel(self, _=None):
        selected_light_level = self.spinBox_light_level.value()
        logging.info(f"Selected Light Level: {selected_light_level}")
        self.debug_console_controller.set_light_level(selected_light_level)

    @asyncSlot()
    async def capture_image_to_local(self):
        with FTPSession(self.ftp_client) as ftp_client:
            # turn off scale and cursor
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, False)
            await LV5600Tasks.capture_n_send_bmp(
                self.telnet_clinet, ftp_client, self.getLocalFilePath()
            )
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True)

    @asyncSlot()
    async def compute_average_mv_sd(self, mode, num_sample=3):
        total_mv = 0
        max_sd = 0
        for i in range(num_sample):
            await self.capture_image_to_local()
            self.display_image(self.getLocalFilePath())
            mv, cursor = self.wfm_image_analysis_controller.compute_mv_cursor(
                self.getLocalFilePath(), mode
            )

            flat_pixel_count = self.app_config_handler.get_flatness_check_pixel()
            sd = self.wfm_image_analysis_controller.get_current_stdev(
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
    @time_it_async
    async def capture_sat_value(self):
        logging.info("-------------------- Capturing Saturation --------------------")
        self.debug_console_controller.set_light_level(200)
        await self.capture_image_to_local()
        mv, cursor = self.wfm_image_analysis_controller.compute_mv_cursor(
            self.getLocalFilePath(), CalculationConstants.NOISE_MODE
        ) #changed to noise mode

        self.app_config_handler.set_target_saturation(mv)
        self.app_config_handler.save_config_to_file()

        # Put the cursor on the waveform
        await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)

        # display the image on the GUI

        self.display_image(self.getLocalFilePath())

        logging.info(f"Saturation Value: {mv} mV")
        self.lcdNumber_sat_target_value.display(mv)

        logging.info(
            "-------------------- Saturation Value Captured --------------------"
        )

    @asyncSlot()
    @time_it_async
    async def classifySat(self):
        # capture an image and classify it
        logging.info("-------------------- Classifying Saturation --------------------")
        mv, cursor, sd = await self.compute_average_mv_sd(CalculationConstants.NOISE_MODE) # CHANGED TO NOISE MODE

        target = self.app_config_handler.get_target_saturation()
        tolerance = self.app_config_handler.get_target_tolerance()
        flat_sv_threshold = self.app_config_handler.get_flatness_check_sv_threshold()
        class_ = self.wfm_image_analysis_controller.classify_waveform(
            mv,
            sd,
            target,
            tolerance,
            flat_sv_threshold,
            CalculationConstants.NOISE_MODE,
        ) # CHANGED TO NOISE MODE
        if class_ == 0:
            class_ = "Over Saturated"
        elif class_ == 1:
            class_ = "Under Saturated"
        elif class_ == 2:
            class_ = "Just Saturated"
        else:
            logging.error("Classification Result is:" + str(class_))
            class_ = "Unknown"

        # turn on scale and cursor
        await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)
        # display the image on the GUI
        await LV5600Tasks.capture_n_send_bmp(
            self.telnet_clinet, self.ftp_client, self.getLocalFilePath()
        )
        self.display_image(self.getLocalFilePath())
        logging.info("Current waveform is: " + class_)
        logging.info(
            "-------------------- Saturation Value Classified --------------------"
        )

    @asyncSlot()
    @time_it_async
    async def setSat(self):
        await self.capture_sat_value()
        logging.info("-------------------- Setting Saturation --------------------")
        final_mv = 0

        light_level_upper_bound = 256
        light_level_lower_bound = 0
        checked_light_levels = set()

        target = self.app_config_handler.get_target_saturation()
        tolerance = self.app_config_handler.get_target_tolerance()
        flat_sv_threshold = self.app_config_handler.get_flatness_check_sv_threshold()

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
                ) # CHANGED TO NOISE MODE
                break

            self.debug_console_controller.set_light_level(middle_light_level)
            time.sleep(0.2)
            logging.info(f"Current Light Level: {middle_light_level}")

            # Using average mv computation when the difference is less than or equal to 4
            if light_level_upper_bound - light_level_lower_bound <= 8:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE
                ) # CHANGED TO NOISE MODE
            else:
                await self.capture_image_to_local()
                self.display_image(self.getLocalFilePath())
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE, 1
                ) # CHANGED TO NOISE MODE

            final_mv = mv
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)
            class_ = self.wfm_image_analysis_controller.classify_waveform(
                mv,
                sd,
                target,
                tolerance,
                flat_sv_threshold,
                CalculationConstants.NOISE_MODE,
            ) # CHANGED TO SAT MODE

            checked_light_levels.add(middle_light_level)
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)

            if class_ == 0:  # over saturated
                light_level_upper_bound = middle_light_level
            elif class_ == 1:
                light_level_lower_bound = middle_light_level
            elif class_ == 2:
                await self.capture_image_to_local()
                self.display_image(self.getLocalFilePath())
                break

        await LV5600Tasks.scale_and_cursor(
            self.telnet_clinet,
            True,
            final_mv / CalculationConstants.CURSOR_TO_MV_FACTOR,
        )
        await LV5600Tasks.capture_n_send_bmp(
            self.telnet_clinet, self.ftp_client, self.getLocalFilePath()
        )
        self.display_image(self.getLocalFilePath())
        logging.info("-------------------- Saturation Value Set --------------------")

    @asyncSlot()
    @time_it_async
    async def captureN1(self):
        logging.info("-------------------- Capturing N1 Value --------------------")

        mv, cursor, sd = await self.compute_average_mv_sd(
            CalculationConstants.NOISE_MODE
        )

        self.app_config_handler.set_target_noise(mv)
        self.app_config_handler.save_config_to_file()

        # Put the cursor on the waveform
        await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)

        # display the image on the GUI
        self.display_image(self.getLocalFilePath())

        logging.info(f"N1 Value: {mv} mV")
        self.lcdNumber_n1value.display(mv)
        self.lcdNumber_n1p20value.display(mv + 20)
        self.lcdNumber_n1m20value.display(mv - 20)

        logging.info("-------------------- N1 Value Captured --------------------")

    @asyncSlot()
    @time_it_async
    async def setNoiseValue(self, offset):
        logging.info("-------------------- Setting Noise Value --------------------")

        light_level_upper_bound = 256
        light_level_lower_bound = 0
        checked_light_levels = set()

        target = self.app_config_handler.get_target_noise() + offset
        tolerance = self.app_config_handler.get_target_tolerance()
        flat_sv_threshold = self.app_config_handler.get_flatness_check_sv_threshold()

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
            time.sleep(0.2)
            logging.info(f"Current Light Level: {middle_light_level}")

            if light_level_upper_bound - light_level_lower_bound <= 8:
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE
                )
            else:
                await self.capture_image_to_local()
                self.display_image(self.getLocalFilePath())
                mv, cursor, sd = await self.compute_average_mv_sd(
                    CalculationConstants.NOISE_MODE, 1
                )

            final_mv = mv
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)
            class_ = self.wfm_image_analysis_controller.classify_waveform(
                mv,
                sd,
                target,
                tolerance,
                flat_sv_threshold,
                CalculationConstants.NOISE_MODE,
            )

            checked_light_levels.add(middle_light_level)
            await LV5600Tasks.scale_and_cursor(self.telnet_clinet, True, cursor)

            if class_ == 0:
                light_level_upper_bound = middle_light_level
            elif class_ == 1:
                light_level_lower_bound = middle_light_level
            elif class_ == 2:
                await self.capture_image_to_local()
                self.display_image(self.getLocalFilePath())
                break

        if offset > 0:
            self.lcdNumber_n1p20value.display(final_mv)
        elif offset < 0:
            self.lcdNumber_n1m20value.display(final_mv)
        else:
            self.lcdNumber_n1value.display(final_mv)

        await LV5600Tasks.scale_and_cursor(
            self.telnet_clinet,
            True,
            final_mv / CalculationConstants.CURSOR_TO_MV_FACTOR,
        )
        await LV5600Tasks.capture_n_send_bmp(
            self.telnet_clinet, self.ftp_client, self.getLocalFilePath()
        )
        self.display_image(self.getLocalFilePath())
        logging.info("-------------------- Noise Value Set --------------------")

    @asyncSlot()
    async def adjust_light_level_precisely(self, mode, current_light_level, target):
        logging.debug("Adjusting light level precisely")
        logging.debug("Target: " + str(target) + " mV")
        logging.debug("Current Light Level: " + str(current_light_level))

        checked_light_levels = set()
        differences = {}

        tolerance = self.app_config_handler.get_target_tolerance()
        flat_pixel_count = self.app_config_handler.get_flatness_check_pixel()
        flat_sv_threshold = self.app_config_handler.get_flatness_check_sv_threshold()

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
                    self.telnet_clinet,
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

            class_ = self.wfm_image_analysis_controller.classify_waveform(
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
                return final_mv
