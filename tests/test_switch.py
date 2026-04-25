"""Tests for TESmart KVM switch entities."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN
from custom_components.tesmart_kvm.coordinator import TesmartKvmCoordinator
from custom_components.tesmart_kvm.switch import TesmartBuzzerSwitch, TesmartInputDetectionSwitch


@pytest.fixture
def coordinator(hass: HomeAssistant) -> TesmartKvmCoordinator:
    """Create a coordinator for switch tests."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="TESmart HKS801-EB23",
        data={
            CONF_MODEL: "HKS801-EB23",
            "host": "192.168.1.10",
            "port": 5000,
        },
        unique_id="192.168.1.10:5000",
    )
    entry.add_to_hass(hass)
    client = AsyncMock()
    return TesmartKvmCoordinator(hass, entry, client)


def test_buzzer_switch_state(coordinator: TesmartKvmCoordinator) -> None:
    """Test buzzer switch state mirrors coordinator state."""
    entity = TesmartBuzzerSwitch(coordinator)

    assert entity.unique_id == f"{coordinator.entry.entry_id}_buzzer"
    assert entity.is_on is None
    coordinator.buzzer_enabled = True
    assert entity.is_on is True
    coordinator.buzzer_enabled = False
    assert entity.is_on is False


async def test_buzzer_switch_turn_on_and_off(coordinator: TesmartKvmCoordinator) -> None:
    """Test buzzer switch actions delegate to coordinator."""
    entity = TesmartBuzzerSwitch(coordinator)
    coordinator.async_set_buzzer = AsyncMock()

    await entity.async_turn_on()
    await entity.async_turn_off()

    coordinator.async_set_buzzer.assert_any_await(True)
    coordinator.async_set_buzzer.assert_any_await(False)
    assert coordinator.async_set_buzzer.await_count == 2


def test_input_detection_switch_state(coordinator: TesmartKvmCoordinator) -> None:
    """Test input detection switch state mirrors coordinator state."""
    entity = TesmartInputDetectionSwitch(coordinator)

    assert entity.unique_id == f"{coordinator.entry.entry_id}_input_detection"
    assert entity.is_on is None
    coordinator.input_detection_enabled = True
    assert entity.is_on is True
    coordinator.input_detection_enabled = False
    assert entity.is_on is False


async def test_input_detection_switch_turn_on_and_off(
    coordinator: TesmartKvmCoordinator,
) -> None:
    """Test input detection switch actions delegate to coordinator."""
    entity = TesmartInputDetectionSwitch(coordinator)
    coordinator.async_set_input_detection = AsyncMock()

    await entity.async_turn_on()
    await entity.async_turn_off()

    coordinator.async_set_input_detection.assert_any_await(True)
    coordinator.async_set_input_detection.assert_any_await(False)
    assert coordinator.async_set_input_detection.await_count == 2
