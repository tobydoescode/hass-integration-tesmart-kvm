"""Constants for the TESmart KVM integration."""

from __future__ import annotations

from dataclasses import dataclass

DOMAIN = "tesmart_kvm"

CONF_MODEL = "model"

DEFAULT_PORT = 5000
DEFAULT_SCAN_INTERVAL = 15

CMD_SWITCH_INPUT = 0x01
CMD_BUZZER = 0x02
CMD_DISPLAY_TIMEOUT = 0x03
CMD_QUERY_INPUT = 0x10
CMD_INPUT_DETECTION = 0x81

DISPLAY_TIMEOUT_OPTIONS: dict[int, str] = {
    0x00: "Always On",
    0x0A: "10 Seconds",
    0x1E: "30 Seconds",
}


@dataclass(frozen=True, slots=True)
class TesmartModelInfo:
    """Information about a TESmart KVM model."""

    name: str
    port_count: int


MODELS: dict[str, TesmartModelInfo] = {
    "HKS801-EB23": TesmartModelInfo(name="HKS801-EB23", port_count=8),
}
