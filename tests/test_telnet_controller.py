import asyncio
import unittest
from unittest.mock import MagicMock, patch
from controllers.telnet_controller import TelnetController

class TestTelnetController(unittest.TestCase):

    def setUp(self):
        self.host = "localhost"
        self.port = 23
        self.username = "testuser"
        self.password = "testpassword"
        self.controller = TelnetController(self.host, self.port, self.username, self.password)

    @staticmethod
    async def async_return(result):
        return result



    @patch("telnetlib3.open_connection")
    def test_connect_error(self, mock_open_connection):
        mock_open_connection.side_effect = Exception("Test error")

        with self.assertRaises(Exception):
            asyncio.run(self.controller.connect())


    @patch("telnetlib3.open_connection")
    def test_login_error(self, mock_open_connection):
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = self.async_return((mock_reader, mock_writer))

        mock_reader.readuntil.side_effect = Exception("Test error")

        with self.assertRaises(Exception):
            asyncio.run(self.controller.connect())
            asyncio.run(self.controller.login())


    @patch("telnetlib3.open_connection")
    def test_send_command_error(self, mock_open_connection):
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = self.async_return((mock_reader, mock_writer))

        mock_writer.write.side_effect = Exception("Test error")

        with self.assertRaises(Exception):
            asyncio.run(self.controller.connect())
            asyncio.run(self.controller.send_command("test command"))

    def test_close(self):
        mock_writer = MagicMock()
        self.controller.writer = mock_writer

        asyncio.run(self.controller.close())

        mock_writer.close.assert_called_once()
