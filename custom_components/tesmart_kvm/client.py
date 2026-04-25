"""Async TCP client for TESmart KVM switches."""

from __future__ import annotations

import asyncio
import contextlib
import logging

from .const import (
    CMD_BUZZER,
    CMD_DISPLAY_TIMEOUT,
    CMD_INPUT_DETECTION,
    CMD_QUERY_INPUT,
    CMD_SWITCH_INPUT,
)

_LOGGER = logging.getLogger(__name__)

PACKET_HEADER = bytes([0xAA, 0xBB, 0x03])
PACKET_FOOTER = bytes([0xEE])
PACKET_LENGTH = 6
TIMEOUT = 5.0
MAX_INPUT_RESPONSE_VALUE = 0x0F
MIN_TCP_PORT = 1
MAX_TCP_PORT = 65535


class TesmartError(Exception):
    """Base exception for TESmart client errors."""


class TesmartConnectionError(TesmartError):
    """Error connecting to or communicating with the device."""


class TesmartProtocolError(TesmartError):
    """Invalid or unexpected response from the device."""


class TesmartClient:
    """Async TCP client for TESmart KVM binary protocol."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        """Return True if connected."""
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        """Open a TCP connection to the device."""
        if not MIN_TCP_PORT <= self._port <= MAX_TCP_PORT:
            raise TesmartConnectionError(f"Invalid TCP port: {self._port}")

        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=TIMEOUT,
            )
        except (OSError, TimeoutError) as err:
            raise TesmartConnectionError(f"Failed to connect to {self._host}:{self._port}") from err

    async def disconnect(self) -> None:
        """Close the TCP connection."""
        if self._writer is not None:
            self._writer.close()
            with contextlib.suppress(OSError):
                await self._writer.wait_closed()
            self._writer = None
            self._reader = None

    def _validate_response(self, cmd: int, response: bytes) -> None:
        """Validate the common 6-byte response packet shape."""
        if not response.startswith(PACKET_HEADER):
            raise TesmartProtocolError(f"Invalid response header: {response.hex()}")
        if not response.endswith(PACKET_FOOTER):
            raise TesmartProtocolError(f"Invalid response footer: {response.hex()}")
        if response[3] != cmd:
            raise TesmartProtocolError(
                f"Unexpected response command: got 0x{response[3]:02x}, expected 0x{cmd:02x}"
            )

    async def _send_command(self, cmd: int, value: int) -> bytes:
        """Send a command and read the 6-byte response."""
        packet = PACKET_HEADER + bytes([cmd, value]) + PACKET_FOOTER

        async with self._lock:
            if not self.connected:
                raise TesmartConnectionError("Not connected")

            assert self._reader is not None
            assert self._writer is not None

            try:
                self._writer.write(packet)
                await self._writer.drain()

                response = await asyncio.wait_for(
                    self._reader.readexactly(PACKET_LENGTH),
                    timeout=TIMEOUT,
                )
                self._validate_response(cmd, response)
            except asyncio.IncompleteReadError as err:
                await self.disconnect()
                raise TesmartConnectionError(
                    f"Incomplete response: got {len(err.partial)} bytes"
                ) from err
            except TesmartProtocolError:
                await self.disconnect()
                raise
            except (OSError, TimeoutError) as err:
                await self.disconnect()
                raise TesmartConnectionError(f"Communication error: {err}") from err

            return response

    async def get_active_input(self) -> int:
        """Query the currently active input port (1-based)."""
        response = await self._send_command(CMD_QUERY_INPUT, 0x00)
        value = response[4]
        if value > MAX_INPUT_RESPONSE_VALUE:
            await self.disconnect()
            raise TesmartProtocolError(f"Invalid active input value: 0x{value:02x}")
        return value + 1  # Response is 0-indexed, we return 1-indexed

    async def set_active_input(self, port: int) -> None:
        """Switch to the specified input port (1-based)."""
        await self._send_command(CMD_SWITCH_INPUT, port)

    async def set_buzzer(self, enabled: bool) -> None:
        """Enable or disable the buzzer."""
        await self._send_command(CMD_BUZZER, 0x01 if enabled else 0x00)

    async def set_display_timeout(self, value: int) -> None:
        """Set the display timeout (0x00=always on, 0x0A=10s, 0x1E=30s)."""
        await self._send_command(CMD_DISPLAY_TIMEOUT, value)

    async def set_input_detection(self, enabled: bool) -> None:
        """Enable or disable auto input detection."""
        value = 0x01 if enabled else 0x00
        await self._send_command(CMD_INPUT_DETECTION, value)

    async def test_connection(self) -> bool:
        """Test connectivity by connecting and querying current input."""
        try:
            await self.connect()
            await self.get_active_input()
        except TesmartError:
            await self.disconnect()
            return False
        await self.disconnect()
        return True
