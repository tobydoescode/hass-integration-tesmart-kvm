# CLAUDE.md

This file provides guidance to Claude Code when working on this repository.

## Project Overview

Home Assistant custom integration for TESmart KVM switches. Communicates with TESmart KVM devices over TCP using their binary protocol to switch inputs, control buzzer/display settings, and monitor active input state.

## Commands

```bash
# Install dependencies
uv sync --extra dev

# Run linter
uv run ruff check custom_components/ tests/

# Fix lint and formatting
uv run ruff check --fix custom_components/ tests/
uv run ruff format custom_components/ tests/

# Run type checker
uv run pyright custom_components/tesmart_kvm/

# Run tests
uv run python -m pytest tests/ -v

# Run tests with coverage
uv run python -m pytest tests/ -v --cov=custom_components.tesmart_kvm --cov-report=term-missing

# Start dev Home Assistant instance
docker compose up -d
```

## Architecture

```
custom_components/tesmart_kvm/
  __init__.py          # Integration setup/teardown, config entry migration
  client.py            # Async TCP client for the TESmart binary protocol
  config_flow.py       # UI config flow for adding devices
  const.py             # Constants, model definitions, command codes
  coordinator.py       # DataUpdateCoordinator that polls device state
  diagnostics.py       # Diagnostics endpoint for debugging
  entity.py            # Base entity class with cached property invalidation
  select.py            # Select entities (active input, display timeout)
  switch.py            # Switch entities (buzzer, input detection)
  strings.json         # Translation strings (source of truth)
  translations/en.json # English translations (must match strings.json)
  manifest.json        # Integration metadata
```

### Key Design Decisions

- **Write-only settings**: Buzzer, display timeout, and input detection are write-only on the device. The coordinator tracks "assumed state" for these -- the value is `None` until the user first sets it.
- **Cached properties**: Entity state properties (`is_on`, `current_option`) use `@cached_property` from `propcache.api` instead of `@property`. The base entity class invalidates these in `_handle_coordinator_update()`.
- **Connection repairs**: The coordinator tracks consecutive poll failures and creates a repair issue after 3 failures. The repair is cleared when the device recovers.
- **Binary protocol**: The client sends 6-byte packets (header `AA BB 03`, command, value, footer `EE`) and expects 6-byte responses. Input values in responses are 0-indexed; the client converts to 1-indexed.
- **Single model support**: Currently only HKS801-EB23 (8-port) is defined in `MODELS`. The architecture supports adding more models by extending the dict in `const.py`.

### Data Flow

1. `__init__.py` creates a `TesmartClient` and `TesmartKvmCoordinator` for each config entry
2. Coordinator is stored in `hass.data[DOMAIN][entry.entry_id]`
3. Coordinator polls `client.get_active_input()` on a 15-second interval
4. Select/switch entities extend `TesmartKvmEntity` (which extends `CoordinatorEntity`)
5. Entity actions (e.g., switch input) call coordinator methods, which call client methods

## Testing

Tests use `pytest-homeassistant-custom-component` with `MockConfigEntry`. The test structure mirrors the source:

- `test_client.py` -- TCP protocol tests with mock asyncio streams
- `test_config_flow.py` -- Config flow UI tests
- `test_coordinator.py` -- Coordinator polling and command tests
- `test_entity.py` -- Base entity device info
- `test_select.py` -- Select entity state and actions
- `test_switch.py` -- Switch entity state and actions

When testing cached properties, invalidate the cache by popping from `entity.__dict__` rather than calling `_handle_coordinator_update()` (which requires a fully wired HA entity).

## CI

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push to main and on PRs:

1. Ruff lint and format check
2. Pyright type checking
3. Pytest with coverage reporting
4. Coverage summary in GitHub step summary
