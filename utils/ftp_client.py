# utils/ftp_client.py
from ftplib import FTP

class FTPClient:
    def __init__(self, host, username, password):
        self.ftp = FTP(host)
        self.ftp.login(username, password)
        self.ftp.set_pasv(True) # set to passive mode, meaning the client will initiate the data connection

    def get_file(self, ftp_file_name, local_file_path):
        with open(local_file_path, 'wb') as local_file:
            self.ftp.retrbinary('RETR ' + ftp_file_name, local_file.write)

    def close(self):
        self.ftp.quit()
