from configparser import ConfigParser


class AppConfig:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config/config.ini")

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
        with open("config/config.ini", "w") as config_file:
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
    