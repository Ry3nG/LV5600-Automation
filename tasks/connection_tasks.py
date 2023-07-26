class ConnectionTask:
    @staticmethod
    async def connect_to_telnet(client):
        await client.connect()
        await client.login()
        return True
    
    @staticmethod
    def connect_to_debugconsole(client):
        if not client.activate():
            return False
        return True