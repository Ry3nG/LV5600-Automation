"""
This module provides a class for connecting to an FTP server and performing file operations.
"""

from ftplib import FTP, error_perm
import logging

class FTPClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None

    def connect(self):
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.username, self.password)
            self.ftp.set_pasv(True)
        except Exception as e:
            logging.error(f"Error while connecting to FTP: {str(e)}")
            self.ftp = None

    def get_file(self, ftp_file_name, local_file_path):
        if not self.ftp:
            logging.error("FTP connection is not established.")
            return

        try:
            with open(local_file_path, 'wb') as local_file:
                self.ftp.retrbinary('RETR ' + ftp_file_name, local_file.write)
        except error_perm as e:
            logging.error(f"Error while downloading file: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")

    def is_connected(self):
        if self.ftp:
            try:
                # An empty string will be returned if the connection is alive
                return self.ftp.voidcmd("NOOP") == ''
            except Exception as e:
                logging.error(f"Error while checking connection status: {str(e)}")
        return False

    def close(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as e:
                logging.error(f"Error while closing FTP connection: {str(e)}")
            finally:
                self.ftp = None
        else:
            logging.error("FTP connection is already closed.")
