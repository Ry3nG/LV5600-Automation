# utils/ftp_client.py
from ftplib import FTP

class FTPClient:
    def __init__(self, host, username, password):
        self.ftp = FTP(host)
        self.ftp.login(username, password)
        self.ftp.set_pasv(True) # set to passive mode, meaning the client will initiate the data connection
    def connect(self):
        self.ftp.connect()

    def get_file(self, ftp_file_name, local_file_path):
        with open(local_file_path, 'wb') as local_file:
            self.ftp.retrbinary('RETR ' + ftp_file_name, local_file.write)

    def is_connected(self):
        try:
            # getwelcome sends a NOOP command to keep the connection alive
            # if the connection is lost, it will throw an exception
            self.ftp.getwelcome()
            return True
        except Exception:
            return False

    def close(self):
        self.ftp.quit()
