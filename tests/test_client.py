"""Tests for the TESmart KVM TCP client."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.tesmart_kvm.client import (
    PACKET_FOOTER,
    PACKET_HEADER,
    TesmartClient,
    TesmartConnectionError,
    TesmartProtocolError,
)
from custom_components.tesmart_kvm.const import (
    CMD_BUZZER,
    CMD_DISPLAY_TIMEOUT,
    CMD_INPUT_DETECTION,
    CMD_QUERY_INPUT,
    CMD_SWITCH_INPUT,
)


def make_response(cmd: int, value: int) -> bytes:
    """Build a mock response packet."""
    return PACKET_HEADER + bytes([cmd, value]) + PACKET_FOOTER


def make_mock_streams(response: bytes) -> tuple[AsyncMock, MagicMock]:
    """Create mock reader/writer for asyncio.open_connection."""
    reader = AsyncMock()
    reader.readexactly = AsyncMock(return_value=response)
    writer = MagicMock()
    writer.is_closing.return_value = False
    writer.write = MagicMock()
    writer.drain = AsyncMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()
    return reader, writer


@pytest.fixture
def client() -> TesmartClient:
    """Create a TesmartClient instance."""
    return TesmartClient("192.168.1.10", 5000)


class TestConnect:
    """Tests for connection handling."""

    async def test_connect_success(self, client: TesmartClient) -> None:
        """Test successful connection."""
        reader, writer = make_mock_streams(b"")
        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            assert client.connected

    async def test_connect_timeout(self, client: TesmartClient) -> None:
        """Test connection timeout raises TesmartConnectionError."""
        with (
            patch("asyncio.open_connection", side_effect=asyncio.TimeoutError),
            pytest.raises(TesmartConnectionError, match="Failed to connect"),
        ):
            await client.connect()

    async def test_connect_refused(self, client: TesmartClient) -> None:
        """Test connection refused raises TesmartConnectionError."""
        with (
            patch("asyncio.open_connection", side_effect=OSError("Connection refused")),
            pytest.raises(TesmartConnectionError, match="Failed to connect"),
        ):
            await client.connect()

    async def test_disconnect(self, client: TesmartClient) -> None:
        """Test disconnect closes the writer."""
        reader, writer = make_mock_streams(b"")
        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.disconnect()
            writer.close.assert_called_once()
            assert not client.connected


class TestCommands:
    """Tests for protocol commands."""

    async def test_get_active_input(self, client: TesmartClient) -> None:
        """Test querying active input sends correct packet and parses response."""
        response = make_response(CMD_QUERY_INPUT, 0x02)  # 0-indexed: 0x02 = input 3
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            result = await client.get_active_input()

        assert result == 3  # 0-indexed response + 1
        expected_packet = PACKET_HEADER + bytes([CMD_QUERY_INPUT, 0x00]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)

    async def test_set_active_input(self, client: TesmartClient) -> None:
        """Test switching input sends correct packet."""
        response = make_response(CMD_SWITCH_INPUT, 0x05)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.set_active_input(5)

        expected_packet = PACKET_HEADER + bytes([CMD_SWITCH_INPUT, 0x05]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)

    async def test_set_buzzer_on(self, client: TesmartClient) -> None:
        """Test enabling buzzer sends correct packet."""
        response = make_response(CMD_BUZZER, 0x01)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.set_buzzer(True)

        expected_packet = PACKET_HEADER + bytes([CMD_BUZZER, 0x01]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)

    async def test_set_buzzer_off(self, client: TesmartClient) -> None:
        """Test disabling buzzer sends correct packet."""
        response = make_response(CMD_BUZZER, 0x00)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.set_buzzer(False)

        expected_packet = PACKET_HEADER + bytes([CMD_BUZZER, 0x00]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)

    async def test_set_display_timeout(self, client: TesmartClient) -> None:
        """Test setting display timeout sends correct packet."""
        response = make_response(CMD_DISPLAY_TIMEOUT, 0x1E)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.set_display_timeout(0x1E)

        expected_packet = PACKET_HEADER + bytes([CMD_DISPLAY_TIMEOUT, 0x1E]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)

    async def test_set_input_detection(self, client: TesmartClient) -> None:
        """Test enabling input detection sends correct packet."""
        response = make_response(CMD_INPUT_DETECTION, 0x01)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            await client.set_input_detection(True)

        expected_packet = PACKET_HEADER + bytes([CMD_INPUT_DETECTION, 0x01]) + PACKET_FOOTER
        writer.write.assert_called_with(expected_packet)
        reader.readexactly.assert_awaited_once_with(6)


class TestErrorHandling:
    """Tests for error handling."""

    async def test_send_command_not_connected(self, client: TesmartClient) -> None:
        """Test sending a command when not connected raises error."""
        with pytest.raises(TesmartConnectionError, match="Not connected"):
            await client.get_active_input()

    async def test_incomplete_response(self, client: TesmartClient) -> None:
        """Test incomplete response disconnects and raises error."""
        reader = AsyncMock()
        reader.readexactly = AsyncMock(
            side_effect=asyncio.IncompleteReadError(partial=b"\xaa\xbb", expected=6)
        )
        writer = MagicMock()
        writer.is_closing.return_value = False
        writer.write = MagicMock()
        writer.drain = AsyncMock()
        writer.close = MagicMock()
        writer.wait_closed = AsyncMock()

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartConnectionError, match="Incomplete response"):
                await client.get_active_input()
            assert not client.connected

    async def test_communication_error_disconnects(self, client: TesmartClient) -> None:
        """Test that OSError during communication triggers disconnect."""
        reader = AsyncMock()
        reader.read = AsyncMock(side_effect=OSError("Connection reset"))
        writer = MagicMock()
        writer.is_closing.return_value = False
        writer.write = MagicMock()
        writer.drain = AsyncMock(side_effect=OSError("Connection reset"))
        writer.close = MagicMock()
        writer.wait_closed = AsyncMock()

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartConnectionError, match="Communication error"):
                await client.get_active_input()

    async def test_invalid_response_header_disconnects(self, client: TesmartClient) -> None:
        """Test invalid response header disconnects and raises protocol error."""
        response = bytes([0x00, 0xBB, 0x03, CMD_QUERY_INPUT, 0x01, 0xEE])
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartProtocolError, match="Invalid response header"):
                await client.get_active_input()
            assert not client.connected

    async def test_invalid_response_footer_disconnects(self, client: TesmartClient) -> None:
        """Test invalid response footer disconnects and raises protocol error."""
        response = bytes([0xAA, 0xBB, 0x03, CMD_QUERY_INPUT, 0x01, 0x00])
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartProtocolError, match="Invalid response footer"):
                await client.get_active_input()
            assert not client.connected

    async def test_unexpected_response_command_disconnects(self, client: TesmartClient) -> None:
        """Test unexpected response command disconnects and raises protocol error."""
        response = make_response(CMD_SWITCH_INPUT, 0x01)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartProtocolError, match="Unexpected response command"):
                await client.get_active_input()
            assert not client.connected

    async def test_out_of_range_active_input_disconnects(self, client: TesmartClient) -> None:
        """Test invalid active input response value raises protocol error."""
        response = make_response(CMD_QUERY_INPUT, 0xFF)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            await client.connect()
            with pytest.raises(TesmartProtocolError, match="Invalid active input value"):
                await client.get_active_input()
            assert not client.connected


class TestConnectionTest:
    """Tests for the test_connection method."""

    async def test_successful_connection_test(self, client: TesmartClient) -> None:
        """Test test_connection returns True on success."""
        response = make_response(CMD_QUERY_INPUT, 0x01)
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            result = await client.test_connection()
            assert result is True

    async def test_failed_connection_test(self, client: TesmartClient) -> None:
        """Test test_connection returns False on failure."""
        with patch("asyncio.open_connection", side_effect=OSError("Connection refused")):
            result = await client.test_connection()
            assert result is False

    async def test_failed_connection_test_disconnects_after_query_error(
        self, client: TesmartClient
    ) -> None:
        """Test test_connection closes a connected socket after query failure."""
        response = bytes([0x00, 0xBB, 0x03, CMD_QUERY_INPUT, 0x01, 0xEE])
        reader, writer = make_mock_streams(response)

        with patch("asyncio.open_connection", return_value=(reader, writer)):
            result = await client.test_connection()

        assert result is False
        writer.close.assert_called_once()
        assert not client.connected
