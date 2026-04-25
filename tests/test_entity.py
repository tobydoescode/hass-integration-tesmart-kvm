"""Tests for TESmart KVM base entity."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.tesmart_kvm.const import CONF_MODEL, DOMAIN
from custom_components.tesmart_kvm.coordinator import TesmartKvmCoordinator
from custom_components.tesmart_kvm.entity import TesmartKvmEntity


@pytest.fixture
def coordinator(hass: HomeAssistant) -> TesmartKvmCoordinator:
    """Create a coordinator for entity tests."""
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


def test_device_info(coordinator: TesmartKvmCoordinator) -> None:
    """Test base entity device info."""
    entity = TesmartKvmEntity(coordinator)

    assert entity.device_info["identifiers"] == {(DOMAIN, coordinator.entry.entry_id)}
    assert entity.device_info["name"] == "TESmart HKS801-EB23"
    assert entity.device_info["manufacturer"] == "TESmart"
    assert entity.device_info["model"] == "HKS801-EB23"
