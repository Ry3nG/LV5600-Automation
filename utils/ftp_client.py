"""
This module provides a class for connecting to an FTP server and performing file operations.
"""

from ftplib import FTP

class FTPClient:
    """
    A class for connecting to an FTP server and performing file operations.

    Attributes:
    -----------
    ftp : FTP
        An instance of the FTP class from the ftplib module.
    """

    def __init__(self, host, username, password):
        """
        Initializes an instance of the FTPClient class.

        Parameters:
        -----------
        host : str
            The hostname or IP address of the FTP server.
        username : str
            The username to use for authentication.
        password : str
            The password to use for authentication.
        """
        self.ftp = FTP(host)
        self.ftp.login(username, password)
        self.ftp.set_pasv(True) # set to passive mode, meaning the client will initiate the data connection

    def connect(self):
        """
        Connects to the FTP server.
        """
        self.ftp.connect()

    def get_file(self, ftp_file_name, local_file_path):
        """
        Downloads a file from the FTP server and saves it to the local file system.

        Parameters:
        -----------
        ftp_file_name : str
            The name of the file to download from the FTP server.
        local_file_path : str
            The path to save the downloaded file on the local file system.
        """
        with open(local_file_path, 'wb') as local_file:
            self.ftp.retrbinary('RETR ' + ftp_file_name, local_file.write)

    def is_connected(self):
        """
        Checks if the FTP client is still connected to the server.

        Returns:
        --------
        bool
            True if the client is still connected, False otherwise.
        """
        try:
            # getwelcome sends a NOOP command to keep the connection alive
            # if the connection is lost, it will throw an exception
            self.ftp.getwelcome()
            return True
        except Exception:
            return False

    def close(self):
        """
        Closes the connection to the FTP server.
        """
        self.ftp.quit()
