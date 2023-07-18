from ftplib import FTP
import logging

class FTPController:
    def __init__(self,host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None
    
    def connect(self):
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.username,self.password)
            self.ftp.set_pasv(True) # passive mode means the server initiates the data connection
            logging.info(f"Connected to FTP server {self.host}")
        except Exception as e:
            logging.error(f"Error while connecting to FTP: {str(e)}")
            raise Exception(f"Error while connecting to FTP: {str(e)}")
    
    def get_file(self, remote_file, local_file):
        if not self.ftp:
            raise ConnectionError("FTP connection is not established.")
        try:
            with open(local_file, 'wb') as file:
                self.ftp.retrbinary(f'RETR {remote_file}', file.write)
        except Exception as e:
            logging.error(f"Error while getting file {remote_file}: {str(e)}")
            raise Exception(f"Error while getting file {remote_file}: {str(e)}")
    
    def is_connected(self):
        if self.ftp:
            try:
                # An empty string will be returned if the connection is alive
                return self.ftp.voidcmd("NOOP") == ''
            except Exception as e:
                logging.error(f"FTP connection is not established: {str(e)}")
                return False
        return False
    
    def close(self):
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