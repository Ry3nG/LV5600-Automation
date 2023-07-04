from PyQt5.QtWidgets import *
from PyQt5 import uic
from qasync import QEventLoop, asyncSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgWidget


import logging
import asyncio
from utils.telnet_client import TelnetClient
from utils.ftp_client import FTPClient
from utils.debug_console_controller import DebugConsoleController

from Constants import Constants

from scripts.capture_and_send_bmp import capture_and_send_bmp
from scripts.recall_preset import recall_preset
from scripts.send_command_terminal import send_command
from scripts.capture_multiple import capture_multiple

from scripts.tune_to_target_light_level import tune_to_target_level
from scripts.lv5600_initialization import (
    lv5600_initialization,
    LV5600InitializationError,
)
from scripts.display_saturation_result import display_result_qt
from scripts.auto_tuning_use_peak_pixel import (
    auto_adjust,
    white_balance_auto_detect,
    noise_level_auto_adjust,
    noise_level_adjust_minus_20,
    noise_level_adjust_plus_20
)

# configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class LogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)


class FTPSession:
    def __init__(self, ftp_client):
        self.ftp_client = ftp_client

    def __enter__(self):
        if not self.ftp_client.is_connected():
            self.ftp_client.connect()
        return self.ftp_client

    def __exit__(self, exc_type, exc, tb):
        if self.ftp_client.is_connected():
            self.ftp_client.close()


class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("LV5600-Automation-GUI.ui", self)
        self.setWindowTitle("LV5600 Automation")
        self.setWindowIcon(QIcon("icon.svg"))
        self.show()

        # initialize telnet client
        self.telnet_client = TelnetClient(
            Constants.IP_ADDRESS_TELNET,
            Constants.TELNET_PORT,
            Constants.USERNAME_TELNET,
            Constants.PASSWORD_TELNET,
        )
        self.ftp_client = FTPClient(
            Constants.IP_ADDRESS_FTP,
            Constants.USERNAME_FTP,
            Constants.PASSWORD_FTP,
        )
        self.debug_console_controller = DebugConsoleController()
        self.n1_mv_value = -1

        log_handler = LogHandler(self.textBrowser)
        log_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(log_handler)

        self.pushButton_2.clicked.connect(self.login)
        self.pushButton_8.clicked.connect(self.establish_connection)
        self.pushButton.clicked.connect(self.clicked_initialize_lv5600)
        self.pushButton_3.clicked.connect(self.clicked_auto_wb)
        self.pushButton_4.clicked.connect(self.clicked_capture_and_classify_sat)
        self.pushButton_5.clicked.connect(self.clicked_auto_adjust_lighting_for_sat)
        self.pushButton_6.clicked.connect(self.clicked_recall_preset)
        self.pushButton_7.clicked.connect(self.clicked_capture_and_send_bmp)
        self.pushButton_9.clicked.connect(self.clicked_auto_adjust_n1_plus_20)
        self.pushButton_10.clicked.connect(self.clicked_auto_adjust_n1_minus_20)

        # Set echo mode to Password for the password line edit
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

    def login(self):
        if self.lineEdit.text() == "LV5600" and self.lineEdit_2.text() == "LV5600":
            # Disable login-related widgets
            self.lineEdit.setEnabled(False)
            self.lineEdit_2.setEnabled(False)
            self.pushButton_2.setEnabled(False)

            self.pushButton_8.setEnabled(True)
        else:
            message = QMessageBox()
            message.setText("Invalid username or password")
            message.exec_()

    def display_image_and_title(self, pixmap, title):
        new_size = self.graphicsView.size()
        pixmap = pixmap.scaled(new_size, Qt.KeepAspectRatio)  # type: ignore

        # Display the QPixmap on QGraphicsView
        scene = QGraphicsScene(self)
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        self.graphicsView.setScene(scene)
        self.graphicsView.fitInView(item)

        # Display the title
        self.label_3.setText(title)

    @asyncSlot()
    async def establish_connection(self):
        try:
            await self.telnet_client.connect()
            logging.info("Telnet connection established")
        except Exception as error:
            logging.error(
                "Error while establishing Telnet connection: %s", lambda: error
            )
            await self.telnet_client.close()
            return

        try:
            if not self.debug_console_controller.activate():
                return
            logging.info("Debug console activated")
        except Exception as error:
            logging.error("Error while activating debug console: %s", lambda: error)
            await self.telnet_client.close()
            return

        # disable connection-related widgets
        self.pushButton_8.setEnabled(False)

        # enable other widgets
        self.graphicsView.setEnabled(True)
        self.pushButton.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)
        self.pushButton_6.setEnabled(True)
        self.pushButton_7.setEnabled(True)
        self.pushButton_9.setEnabled(True)
        self.pushButton_10.setEnabled(True)
        self.textBrowser.setEnabled(True)
        self.label_3.setEnabled(True)

    @asyncSlot()
    async def clicked_initialize_lv5600(self):
        logging.info(" ------------- Initializing LV5600 -------------")
        await lv5600_initialization(self.telnet_client)
        logging.info(" ------------- LV5600 initialized -------------")

    @asyncSlot()
    async def clicked_auto_wb(self):
        logging.info(" ------------- Starting Auto White Balance -------------")
        with FTPSession(self.ftp_client) as ftp_client:
           self.n1_mv_value = await white_balance_auto_detect(self.telnet_client, ftp_client)
        
        await self.clicked_capture_and_send_bmp()
        logging.info(" ------------- Auto White Balance Finished -------------")


    @asyncSlot()
    async def clicked_capture_and_classify_sat(self):
        logging.info(
            " ------------- Starting Capture and Classify Saturation -------------"
        )
        with FTPSession(self.ftp_client) as ftp_client:
            pixmap, saturation_class, current_mv_value = await display_result_qt(
                self.telnet_client, ftp_client
            )

            # Display the result
            self.display_image_and_title(pixmap, saturation_class)

        logging.info(
            " ------------- Capture and Classify Saturation Finished -------------"
        )

    @asyncSlot()
    async def clicked_auto_adjust_lighting_for_sat(self):
        logging.info(
            " ------------- Starting Auto Adjust Lighting for Saturation -------------"
        )
        current_light_level,ok = QInputDialog.getInt(self, 'Input Dialog', "Enter the current light level: ",min=0,max=255)
        if ok:
            with FTPSession(self.ftp_client) as ftp_client:
                await auto_adjust(self.telnet_client, ftp_client,self.debug_console_controller,current_light_level,mode = "SAT",target=769.5,target_high_threshold=769.5,target_low_threshold=766.5,use_poly_prediction=True,jump_threshold=700,use_qt=True)
        
        await self.clicked_capture_and_send_bmp()
        logging.info(
            " ------------- Auto Adjust Lighting for Saturation Finished -------------"
        )

    @asyncSlot()
    async def clicked_recall_preset(self):
        # prompt user to enter preset number
        preset_number, ok = QInputDialog.getInt(
            self, "Input Dialog", "Enter the preset number: ", min=0, max=255
        )
        if ok:
            logging.info(
                " ------------- Starting Recall Preset %s -------------", preset_number
            )
            await recall_preset(self.telnet_client,preset_number)
            logging.info(
                " ------------- Recall Preset %s Finished -------------", preset_number
            )

    @asyncSlot()
    async def clicked_capture_and_send_bmp(self):
        logging.info(" ------------- Starting Capture and Send BMP -------------")
        with FTPSession(self.ftp_client) as ftp_client:
            await capture_and_send_bmp(self.telnet_client, ftp_client)
            # display in graphicsView
            pixmap = QPixmap(Constants.LOCAL_FILE_PATH_BMP)
            self.display_image_and_title(pixmap, "Screenshot")

        logging.info(" ------------- Capture and Send BMP Finished -------------")
    
    @asyncSlot()
    async def clicked_auto_adjust_n1_plus_20(self):
        logging.info("------------- Starting Auto Adjust Lighting for Noise (n1+20mV) -------------")
        if self.n1_mv_value == -1:
            message = QMessageBox()
            message.setText("Please run Auto WB first")
            message.exec_()
            return
        else:
            logging.info("n1_mv_value: %s", self.n1_mv_value)

        current_light_level, ok = QInputDialog.getInt(self, 'Input Dialog', "Enter the current light level: ", min=0, max=255)
        if not ok:
            return

        with FTPSession(self.ftp_client) as ftp_client:
            await noise_level_adjust_plus_20(self.telnet_client, ftp_client, self.debug_console_controller, self.n1_mv_value, current_light_level)

        await self.clicked_capture_and_send_bmp()
        logging.info("------------- Auto Adjust Lighting for Noise (n1+20mV) Finished -------------")
    
    @asyncSlot()
    async def clicked_auto_adjust_n1_minus_20(self):
        logging.info("------------- Starting Auto Adjust Lighting for Noise (n1-20mV) -------------")
        if self.n1_mv_value == -1:
            message = QMessageBox()
            message.setText("Please run Auto WB first")
            message.exec_()
            return
        else:
            logging.info("n1_mv_value: %s", self.n1_mv_value)


        current_light_level, ok = QInputDialog.getInt(self, 'Input Dialog', "Enter the current light level: ", min=0, max=255)
        if not ok:
            return

        with FTPSession(self.ftp_client) as ftp_client:
            await noise_level_adjust_minus_20(self.telnet_client, ftp_client, self.debug_console_controller, self.n1_mv_value,current_light_level)

        await self.clicked_capture_and_send_bmp()
        logging.info("------------- Auto Adjust Lighting for Noise (n1-20mV) Finished -------------")


async def main():
    app = QApplication([])
    llop = QEventLoop(app)
    asyncio.set_event_loop(llop)

    window = MyGUI()
    with llop:
        llop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
