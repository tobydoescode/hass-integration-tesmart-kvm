"""Fixtures for TESmart KVM integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.tesmart_kvm.client import PACKET_FOOTER, PACKET_HEADER
from custom_components.tesmart_kvm.const import CONF_MODEL

MOCK_HOST = "192.168.1.10"
MOCK_PORT = 5000

MOCK_CONFIG_DATA = {
    CONF_MODEL: "HKS801-EB23",
    "host": MOCK_HOST,
    "port": MOCK_PORT,
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:  # noqa: ARG001
    """Enable custom integrations for all tests."""


def make_response(cmd: int, value: int) -> bytes:
    """Build a 6-byte TESmart response packet."""
    return PACKET_HEADER + bytes([cmd, value]) + PACKET_FOOTER


@pytest.fixture
def mock_client() -> Generator[AsyncMock]:
    """Mock the TesmartClient."""
    with patch(
        "custom_components.tesmart_kvm.client.TesmartClient",
        autospec=True,
    ) as mock_cls:
        client = mock_cls.return_value
        client.connected = True
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()
        client.get_active_input = AsyncMock(return_value=1)
        client.set_active_input = AsyncMock()
        client.set_buzzer = AsyncMock()
        client.set_display_timeout = AsyncMock()
        client.set_input_detection = AsyncMock()
        client.test_connection = AsyncMock(return_value=True)
        yield client
