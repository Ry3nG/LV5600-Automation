from configparser import ConfigParser
import logging
import os
import sys
from PyQt5 import QtCore


class AppConfig(QtCore.QObject):
    settings_changed = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config = ConfigParser()
        # determine if the application is a script file or frozen exe
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS  # type: ignore
            config_file_path = os.path.join(application_path, "config", "config.ini")
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(application_path, "config.ini")

        self.config.read(config_file_path)

        # execute default settings
        self.set_default_settings()

    def get_telnet_address(self):
        return self.config.get("telnet", "host")

    def get_telnet_port(self):
        return self.config.getint("telnet", "port")

    def get_telnet_username(self):
        return self.config.get("telnet", "username")

    def get_telnet_password(self):
        return self.config.get("telnet", "password")

    def set_telnet_address(self, address):
        self.config.set("telnet", "host", address)
        self.settings_changed.emit()

    def set_telnet_port(self, port):
        self.config.set("telnet", "port", str(port))
        self.settings_changed.emit()

    def set_telnet_username(self, username):
        self.config.set("telnet", "username", username)
        self.settings_changed.emit()

    def set_telnet_password(self, password):
        self.config.set("telnet", "password", password)
        self.settings_changed.emit()

    def get_ftp_address(self):
        return self.config.get("ftp", "host")

    def get_ftp_username(self):
        return self.config.get("ftp", "username")

    def get_ftp_password(self):
        return self.config.get("ftp", "password")

    def set_ftp_address(self, address):
        self.config.set("ftp", "host", address)
        self.settings_changed.emit()

    def set_ftp_username(self, username):
        self.config.set("ftp", "username", username)
        self.settings_changed.emit()

    def set_ftp_password(self, password):
        self.config.set("ftp", "password", password)
        self.settings_changed.emit()

    def save_config_to_file(self):
        if getattr(sys, "frozen", False):
            application_path = sys._MEIPASS  # type: ignore
            config_file_path = os.path.join(application_path, "config", "config.ini")
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(application_path, "config.ini")

        with open(config_file_path, "w") as config_file:
            self.config.write(config_file)
            self.settings_changed.emit()

    def get_local_file_path(self):
        return self.config.get("file", "local_file_path")

    def set_local_file_path(self, local_file_path):
        self.config.set("file", "local_file_path", local_file_path)
        self.settings_changed.emit()

    def get_target_tolerance(self):
        return self.config.getfloat("constants", "target_tolerance")

    def set_target_tolerance(self, target_tolerance):
        self.config.set("constants", "target_tolerance", str(target_tolerance))
        self.settings_changed.emit()

    def get_target_saturation(self):
        return self.config.getfloat("constants", "target_saturation_mV")

    def set_target_saturation(self, target_saturation):
        self.config.set("constants", "target_saturation_mV", str(target_saturation))
        self.settings_changed.emit()

    def set_flatness_check_pixel(self, flatness_check_threshold):
        self.config.set(
            "constants", "flatness_check_pixel", str(flatness_check_threshold)
        )
        self.settings_changed.emit()

    def get_flatness_check_pixel(self):
        return self.config.getfloat("constants", "flatness_check_pixel")

    def set_flatness_check_sv_threshold(self, flatness_check_sv_threshold):
        self.config.set(
            "constants", "flatness_check_sv_threshold", str(flatness_check_sv_threshold)
        )
        self.settings_changed.emit()

    def get_flatness_check_sv_threshold(self):
        return self.config.getfloat("constants", "flatness_check_sv_threshold")

    def get_line_number(self):
        return self.config.get("lv5600", "line_number")

    def set_line_number(self, line_number):
        self.config.set("lv5600", "line_number", str(line_number))
        self.settings_changed.emit()

    def get_current_settings(self):
        current_settings = ""
        current_settings += "Telnet Host: " + self.get_telnet_address() + "\n"
        current_settings += "Telnet Port: " + str(self.get_telnet_port()) + "\n"
        current_settings += "Telnet Username: " + self.get_telnet_username() + "\n"
        current_settings += "Telnet Password: " + self.get_telnet_password() + "\n"
        current_settings += "FTP Host: " + self.get_ftp_address() + "\n"
        current_settings += "FTP Username: " + self.get_ftp_username() + "\n"
        current_settings += "FTP Password: " + self.get_ftp_password() + "\n"
        current_settings += "Local File Path: " + self.get_local_file_path() + "\n"
        current_settings += (
            "Target Tolerance: " + str(self.get_target_tolerance()) + "\n"
        )
        current_settings += (
            "Target Saturation: " + str(self.get_target_saturation()) + "\n"
        )
        current_settings += (
            "Flatness Check Pixel: " + str(self.get_flatness_check_pixel()) + "\n"
        )
        current_settings += (
            "Flatness Check SV Threshold: "
            + str(self.get_flatness_check_sv_threshold())
            + "\n"
        )
        current_settings += "Line Number: " + self.get_line_number() + "\n"
        return current_settings

    def set_default_settings(self):
        self.set_telnet_address("192.168.0.1")
        self.set_telnet_port(23)
        self.set_telnet_username("LV5600")
        self.set_telnet_password("LV5600")
        self.set_ftp_address("192.168.0.1")
        self.set_ftp_username("LV5600")
        self.set_ftp_password("LV5600")
        self.set_local_file_path("C://LV5600-OCB_Automation")
        self.set_target_tolerance(0.02)
        self.set_target_saturation(763.3)
        self.set_flatness_check_pixel(10.0)
        self.set_flatness_check_sv_threshold(0.5)
        self.set_line_number(580)
        self.save_config_to_file()
