import asyncio
import unittest
from unittest.mock import patch, MagicMock
from utils.telnet_client import TelnetClient

class TestTelnetClient(unittest.TestCase):
    @patch('utils.telnet_client.telnetlib3.open_connection')
    async def test_connect(self, mock_open_connection):
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        client = TelnetClient('localhost', 23, 'user', 'pass')
        await client.connect()

        mock_open_connection.assert_called_once_with('localhost', 23)
        mock_writer.write.assert_called_once_with('user\r\n')
        mock_reader.readuntil.assert_called_once_with(b'Password:')
        mock_writer.write.assert_called_with('pass\r\n')
        mock_reader.readuntil.assert_called_with(b'\n')
        mock_writer.close.assert_not_called()

    @patch('utils.telnet_client.telnetlib3.open_connection')
    async def test_send_command(self, mock_open_connection):
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        client = TelnetClient('localhost', 23, 'user', 'pass')
        await client.connect()

        response = await client.send_command('ls')
        mock_writer.write.assert_called_once_with('ls\r\n')
        mock_reader.readuntil.assert_called_once_with(b'\n')
        self.assertEqual(response, mock_reader.readuntil.return_value)

        mock_writer.close.assert_not_called()

    @patch('utils.telnet_client.telnetlib3.open_connection')
    async def test_close(self, mock_open_connection):
        mock_reader = MagicMock()
        mock_writer = MagicMock()
        mock_open_connection.return_value = (mock_reader, mock_writer)

        client = TelnetClient('localhost', 23, 'user', 'pass')
        await client.connect()

        await client.close()

        mock_writer.close.assert_called_once()