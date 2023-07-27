class ConnectionTask:
    @staticmethod
    async def connect_to_telnet(client):
        """
        Connects to a telnet client and logs in.

        Args:
            client: A telnet client object.

        Returns:
            True if the connection and login were successful, False otherwise.
        """
        await client.connect()
        await client.login()
        return True
    
    @staticmethod
    def connect_to_debugconsole(client):
        """
        Connects to a debug console client.

        Args:
            client: A debug console client object.

        Returns:
            True if the connection was successful, False otherwise.
        """
        if not client.activate():
            return False
        return True