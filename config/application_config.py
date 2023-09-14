from configparser import ConfigParser
import logging
import os
import sys


class AppConfig:
    def __init__(self):
        self.config = ConfigParser()
        # determine if the application is a script file or frozen exe
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS # type: ignore
            config_file_path = os.path.join(application_path, 'config','config.ini')
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(application_path,'config.ini')

        self.config.read(config_file_path)
        logging.debug("Config file path: " + config_file_path)
        logging.debug("Config file contents: ")
        for section in self.config.sections():
            logging.debug(section)
            for key in self.config[section]:
                logging.debug(key + ": " + self.config[section][key])
        

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

    def set_telnet_port(self, port):
        self.config.set("telnet", "port", str(port))

    def set_telnet_username(self, username):
        self.config.set("telnet", "username", username)

    def set_telnet_password(self, password):
        self.config.set("telnet", "password", password)

    def get_ftp_address(self):
        return self.config.get("ftp", "host")

    def get_ftp_username(self):
        return self.config.get("ftp", "username")

    def get_ftp_password(self):
        return self.config.get("ftp", "password")

    def set_ftp_address(self, address):
        self.config.set("ftp", "host", address)

    def set_ftp_username(self, username):
        self.config.set("ftp", "username", username)

    def set_ftp_password(self, password):
        self.config.set("ftp", "password", password)

    def save_config_to_file(self):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS # type: ignore
            config_file_path = os.path.join(application_path, 'config', 'config.ini')
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
            config_file_path = os.path.join(application_path, 'config.ini')
        
        with open(config_file_path, "w") as config_file:
            self.config.write(config_file)


    def get_local_file_path(self):
        return self.config.get("file", "local_file_path")

    def set_local_file_path(self, local_file_path):
        self.config.set("file", "local_file_path", local_file_path)

    def get_target_tolerance(self):
        return self.config.getfloat("constants", "target_tolerance")

    def set_target_tolerance(self, target_tolerance):
        self.config.set("constants", "target_tolerance", str(target_tolerance))

    def get_target_saturation(self):
        return self.config.getfloat("constants", "target_saturation_mV")
    
    def set_target_saturation(self, target_saturation):
        self.config.set("constants", "target_saturation_mV", str(target_saturation))

    def set_flatness_check_pixel(self, flatness_check_threshold):
        self.config.set("constants", "flatness_check_pixel", str(flatness_check_threshold))
    
    def get_flatness_check_pixel(self):
        return self.config.getfloat("constants", "flatness_check_pixel")
    
    def set_flatness_check_sv_threshold(self, flatness_check_sv_threshold):
        self.config.set("constants", "flatness_check_sv_threshold", str(flatness_check_sv_threshold))
    
    def get_flatness_check_sv_threshold(self):
        return self.config.getfloat("constants", "flatness_check_sv_threshold")
    
    
    def get_line_number(self):
        return self.config.get("lv5600", "line_number")
    
    def set_line_number(self, line_number):
        self.config.set("lv5600", "line_number", str(line_number))