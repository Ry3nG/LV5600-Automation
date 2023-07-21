"""
    This file contains the FTPController class that can be used to control an FTP server. The class provides methods to connect to the server, download files, and close the connection. The module requires the ftplib library to be installed.
"""
from ftplib import FTP
import logging

class FTPController:
    def __init__(self,host, username, password):
        """
        Initializes an instance of the FTPController class with the given host, username, and password.

        Args:
        - host (str): The hostname or IP address of the FTP server.
        - username (str): The username to use for authentication.
        - password (str): The password to use for authentication.
        """
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None
    
    def connect(self):
        """
        Connects to the FTP server using the provided credentials.

        Raises:
        - Exception: If there is an error while connecting to the FTP server.
        """
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.username,self.password)
            self.ftp.set_pasv(True) # passive mode means the server initiates the data connection
            logging.info(f"Connected to FTP server {self.host}")
        except Exception as e:
            logging.error(f"Error while connecting to FTP: {str(e)}")
            raise Exception(f"Error while connecting to FTP: {str(e)}")
    
    def get_file(self, remote_file, local_file):
        """
        Downloads a file from the FTP server to the local file system.

        Args:
        - remote_file (str): The path to the file on the FTP server.
        - local_file (str): The path to the file on the local file system.

        Raises:
        - ConnectionError: If the FTP connection is not established.
        - Exception: If there is an error while downloading the file.
        """
        if not self.ftp:
            raise ConnectionError("FTP connection is not established.")
        try:
            with open(local_file, 'wb') as file:
                self.ftp.retrbinary(f'RETR {remote_file}', file.write)
        except Exception as e:
            logging.error(f"Error while getting file {remote_file}: {str(e)}")
            raise Exception(f"Error while getting file {remote_file}: {str(e)}")
    
    def is_connected(self):
        """
        Checks if the FTP connection is still alive.

        Returns:
        - bool: True if the connection is alive, False otherwise.
        """
        if self.ftp:
            try:
                # An empty string will be returned if the connection is alive
                return self.ftp.voidcmd("NOOP") == ''
            except Exception as e:
                logging.error(f"FTP connection is not established: {str(e)}")
                return False
        return False
    
    def close(self):
        """
        Closes the FTP connection.

        Raises:
        - ConnectionError: If the FTP connection is not established.
        - Exception: If there is an error while closing the connection.
        """
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception as e:
                logging.error(f"Error while closing FTP connection: {str(e)}")
                raise Exception(f"Error while closing FTP connection: {str(e)}")
            finally:
                self.ftp = None
        else:
            logging.error("Error closing FTP connection: FTP connection is not established.")
            raise ConnectionError("FTP connection is not established.")