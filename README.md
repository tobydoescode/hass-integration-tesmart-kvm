# Home Assistant TESmart KVM Integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tobydoescode&repository=ha-integration-tesmart-kvm&category=integration)

A [HACS](https://hacs.xyz)-compatible custom integration that controls [TESmart](https://www.tesmart.com) KVM switches over the local network.

## Features

Each configured KVM becomes an HA device with:

- **Select** — active input port, display timeout (Always On / 10s / 30s)
- **Switch** — buzzer, auto input detection

## Supported models

| Model | Ports |
|---|---|
| HKS801-EB23 | 8 |

Other TESmart models may work but have not been tested. To request support, open an issue with the model number and protocol documentation.

## Installation

### HACS (recommended)

1. Open HACS in your Home Assistant instance
2. Go to **Integrations** → **Custom repositories**
3. Add this repository URL and select **Integration** as the category
4. Install **TESmart KVM** and restart Home Assistant

### Manual

Copy the `custom_components/tesmart_kvm` directory into your Home Assistant `config/custom_components/` directory and restart.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **TESmart KVM**
3. Configure:
   - **Model** — your KVM model
   - **Host** — IP address or hostname of the KVM
   - **Port** — TCP port (default `5000`)

The integration polls the KVM every 15 seconds for the active input.

## Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Task](https://taskfile.dev) — task runner
- [Docker](https://www.docker.com) — for the dev HA instance

### Commands

| Command | Description |
|---|---|
| `task sync` | Install Python dependencies |
| `task lint` | Run ruff linter and format check |
| `task lint:fix` | Auto-fix lint and formatting issues |
| `task test` | Run pytest |
| `task dev` | Start Home Assistant in Docker |
| `task dev:stop` | Stop Home Assistant |
| `task dev:restart` | Restart Home Assistant (after code changes) |
| `task dev:logs` | Tail Home Assistant logs |

### Testing with a real device

1. **Start Home Assistant:**

   ```bash
   task dev
   ```

   Open http://localhost:8123 and complete the onboarding.

2. **Add the integration:**

   Go to **Settings → Devices & Services → Add Integration → TESmart KVM** and enter the model, host, and port of your KVM.

3. **Verify:**

   Go to **Settings → Devices & Services → TESmart KVM**. You should see a device with:
   - Active Input select (1 through N ports)
   - Display Timeout select
   - Buzzer switch
   - Input Detection switch

4. **Clean up:**

   ```bash
   task dev:stop
   ```
