class FTPSession:
    def __init__(self,ftp_client):
        self.ftp_client = ftp_client
    
    def __enter__(self):
        if not self.ftp_client.is_connected():
            self.ftp_client.connect()
        return self.ftp_client
    
    def __exit__(self, exc_type, exc,tb):
        if self.ftp_client.is_connected():
            self.ftp_client.close()