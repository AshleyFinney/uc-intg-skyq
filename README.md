# SkyQ Integration for Unfolded Circle Remote 2/3

Control your SkyQ satellite boxes directly from your Unfolded Circle Remote 2 or Remote 3 with comprehensive remote control functionality, **multi-device support**, and **real-time status monitoring**.

![SkyQ](https://img.shields.io/badge/SkyQ-Satellite%20TV-blue)
![License](https://img.shields.io/badge/license-MPL--2.0-blue?style=flat-square)

---

## ⚠️ Personal Fork Notice

This is a **personal fork** of [mase1981/uc-intg-skyq](https://github.com/mase1981/uc-intg-skyq), maintained for use on a single Sky Q **ES240** box. **Other Sky Q variants are explicitly not supported by this fork** — for broader hardware support, please use the upstream project instead.

All credit for the original implementation goes to **[Meir Miyara](https://www.linkedin.com/in/meirmiyara)**, who built and continues to maintain the upstream integration. They've done a fantastic job creating it without owning a Sky Q box of their own — please [support their work](https://buymeacoffee.com/meirmiyara) if you find this integration useful:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Meir%20a%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/meirmiyara)
[![PayPal](https://img.shields.io/badge/PayPal%20Meir-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/mmiyara)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor%20Meir-GitHub-pink?style=for-the-badge&logo=github)](https://github.com/sponsors/mase1981)

The upstream project is welcome to reference any changes in this fork.

---

## Differences from upstream

User-facing fixes and improvements in this fork.

### Bug fixes

- **Digit buttons no longer fire twice.** Number presses on custom UI pages no longer double-trigger or end with a phantom `OK`.
- **Concurrent channel changes are safe.** Mashing channel buttons or overlapping `channel_select:` activations no longer tunes to an unpredictable channel.
- **Channel changes feel snappier.** Channel-up/down and `channel_select:` presses no longer block the UI.
- **Faster media browsing.** Channels, favourites, and recordings load in parallel.
- **Radio channels display their "Radio" subtitle correctly.**
- **Channel dropdown is reliable.** Channels no longer go silently missing from the list.
- **Recordings list is honest about playback.** The recordings entry no longer claims to be playable — see the recordings caveat below.
- **Shuffle / Repeat buttons no longer pop an error toast.** Tapping them silently does nothing now, since Sky Q has no shuffle/repeat concept.

### New entities

- **Four Select dropdown widgets**, each rendering as an independent home-screen entry:
  - **Channels** — full TV-channel list with one-tap tuning
  - **Radio** — split out from Channels so radio stations have their own dropdown
  - **Favourites** — your Sky Q favourites list with one-tap tuning
  - **Recordings** — informational list of all recordings
- **Six new sensors:** Serial Number, Software Version, HDR Capable, UHD Capable, Uptime (formatted as `Xh Ym` / `Xd Yh Zm`), and Media Kind (`Live` / `Recording` / `App`).
- **Recordings grouped by series in the media browser.** Multi-episode shows collapse into folders and drilling in lists episodes as `S01E01`, `S01E02`… sorted by season → episode → air date. Single-recording titles stay as flat items at the top level.

### Caveats

- **Apps cannot be launched programmatically on Sky Q.** The box exposes no app-launch endpoint, so there's no Apps dropdown. Use the Remote's button mappings to navigate the on-screen apps menu if you need to launch one.
- **Recordings can only be browsed, not played remotely.** Sky Q doesn't expose a way to start playback of a specific recording from outside the box's UI.

### Note on uptime

The Uptime sensor reads Sky Q's `systemUptime` field, which counts time since the box last woke from deep standby — *not* since the last full power cycle. So it typically reads in hours rather than days or weeks, by Sky's design.

For the full commit log including internal cleanups, see [the main branch](https://github.com/AshleyFinney/uc-intg-skyq/commits/main).

---

## Features

This integration provides full remote control of your Sky Q satellite box directly from your Unfolded Circle Remote, with automatic multi-device detection and comprehensive remote functionality. This fork is used daily on a Sky Q **ES240** — no other variants have been tested by the fork maintainer.

### 📺 **Multi-Device Support**

- **Multi-Device Setup** - Configure up to 10 Sky Q devices in a single integration
- **Smart Naming** - Automatic entity naming using device information returned by the box
- **Single Tested Model** - This fork is only tested on **ES240**. The upstream integration supports other variants (ES130, ES200, etc.) — use it instead if you have one of those.

#### **Per-Device Entities**
Each SkyQ device creates several entities:
- **Remote**: Full button control with 4 UI pages
- **Media Player**: Playback transport, source list, browse view (with series-grouped recordings, channel logos, thumbnails)
- **Selects**: Channels, Radio, Favourites, Recordings — independent dropdown widgets
- **Sensors**: Model, IP, Serial, Software Version, HDR / UHD capable, Uptime, Channel, Connection Type, Media Kind

### 🎮 **Remote Control Functionality**

#### **Comprehensive Button Support**
Real SkyQ protocol implementation with confirmed working buttons:

**Power Control** (3 commands):
- **Power Toggle**, **Power On**, **Off** - Complete power management

**Navigation** (8 commands):
- **D-Pad**: Up, Down, Left, Right, Select - Menu navigation
- **Control**: Back, Home, Services - Interface navigation

**Playback Control** (6 commands):
- **Transport**: Play, Pause, Stop, Record, Fast Forward, Rewind
- **Live TV**: Full control of live playback and recording

**Channel Control**:
- **Number Pad** (0-9) + Select - Direct channel entry
- **Channel Up / Down** - Channel navigation
- **Guide**, **Info** - Program information and TV guide

**Volume Control** (3 commands):
- **Volume Up/Down**, **Mute Toggle** - Audio control

**Color Buttons** (4 commands):
- **Red**, **Green**, **Yellow**, **Blue** - Interactive TV functions

**Special Functions** (8 commands):
- **Sky Button**, **Search**, **Text/Teletext**, **Help**, **Services**, **Menu**, **Guide**, **Info**

#### **User Interface Features**
- **4 Comprehensive UI Pages**: Main Control, Numbers, Color Buttons, Special Functions
- **On-Screen Remote**: Full remote interface displayed on Remote screen
- **Button Mapping**: Physical Remote button mapping for core functions
- **Simple Commands**: All buttons available as simple command shortcuts

### **Device Requirements**

#### **Sky Q Device Compatibility**
- **Tested Model**: Sky Q **ES240** (UK). The integration may work on other Sky Q variants (ES130, ES200, etc.) since the protocol is shared, but no other models are tested or supported by this fork — use the [upstream project](https://github.com/mase1981/uc-intg-skyq) for broader compatibility.
- **Firmware**: Any current Sky Q firmware version
- **Network**: Ethernet or Wi-Fi connected Sky Q device
- **API Access**: Standard Sky Q HTTP and TCP remote protocols (enabled by default)

### **Protocol Requirements**

- **Protocol**: SkyQ HTTP API + TCP Remote Control
- **HTTP Port**: 9006 (or 8080 for some devices)
- **Remote Port**: 49160 (default)
- **Network Access**: Device must be on same local network
- **Connection**: Real-time remote control commands

### **Network Requirements**

- **Local Network Access** - Integration requires same network as SkyQ devices
- **Port Access**: HTTP API (port 9006 or 8080) and Remote Control (port 49160)
- **Firewall**: No special configuration required for standard home networks
- **Static IP Recommended** - Device should have static IP or DHCP reservation

## Installation

### Option 1: Remote Web Interface (Recommended)
1. Open the [**latest release**](https://github.com/AshleyFinney/uc-intg-skyq/releases/latest)
2. Download the `uc-intg-skyq-<version>-aarch64.tar.gz` asset
3. Open your remote's web interface (`http://your-remote-ip`)
4. Go to **Settings** → **Integrations** → **Add Integration**
5. Click **Upload** and select the downloaded `.tar.gz` file

> Prefer the upstream build? Use [mase1981/uc-intg-skyq's releases](https://github.com/mase1981/uc-intg-skyq/releases) instead — recommended if you don't have an ES240.

### Option 2: Docker (Advanced Users)

The fork publishes a pre-built Docker image as a side effect of the release workflow:

**Image**: `ghcr.io/ashleyfinney/uc-intg-skyq:latest`

**Docker Compose:**
```yaml
services:
  uc-intg-skyq:
    image: ghcr.io/ashleyfinney/uc-intg-skyq:latest
    container_name: uc-intg-skyq
    network_mode: host
    volumes:
      - </local/path>:/data
    environment:
      - UC_CONFIG_HOME=/data
      - UC_INTEGRATION_HTTP_PORT=9090
      - UC_INTEGRATION_INTERFACE=0.0.0.0
      - PYTHONPATH=/app
    restart: unless-stopped
```

**Docker Run:**
```bash
docker run -d --name uc-skyq --restart unless-stopped --network host -v skyq-config:/app/config -e UC_CONFIG_HOME=/app/config -e UC_INTEGRATION_INTERFACE=0.0.0.0 -e UC_INTEGRATION_HTTP_PORT=9090 -e PYTHONPATH=/app ghcr.io/ashleyfinney/uc-intg-skyq:latest
```

## Configuration

### Step 1: Prepare Your SkyQ Devices

**IMPORTANT**: SkyQ devices must be powered on and connected to your network before adding the integration.

#### Verify Network Connection:
1. Ensure SkyQ devices are powered on and connected to network
2. Note the IP address for each device
3. Verify devices are accessible on network
4. Recommended: Give static IP addresses to your SkyQ devices

#### Network Setup:
- **Wired Connection**: Recommended for stability
- **Static IP**: Recommended via DHCP reservation
- **Firewall**: Allow HTTP traffic on ports 9006/8080 and 49160
- **Network Isolation**: Must be on same subnet as Remote

### Step 2: Setup Integration

1. After installation, go to **Settings** → **Integrations**
2. The SkyQ integration should appear in **Available Integrations**
3. Click **"Configure"** to begin setup:

#### **Device Count Selection:**
- Choose number of SkyQ devices to configure (1-10)

#### **Device Configuration:**
For each device:
- **Device IP Address**: SkyQ device IP (e.g., 192.168.1.100 or 192.168.1.100:9006)
- **Device Name**: Location-based name (e.g., "Living Room SkyQ", "Kitchen SkyQ")
- Click **Complete Setup**

#### **Connection Test:**
- Integration verifies device connectivity
- Tests HTTP API and remote control access
- Setup fails if device unreachable

4. Integration will create remote entities for each device:
   - **Remote**: `[Device Name] Remote ([Model])`

## Using the Integration

### Remote Entity

The remote entity provides comprehensive device control:

- **Power Control**: Power On/Off/Toggle/Standby
- **Navigation**: D-Pad and menu controls
- **Playback**: Transport controls and recording
- **Channel Control**: Number pad and channel navigation
- **Volume**: Volume and mute controls
- **Color Buttons**: Interactive TV functions
- **Special Functions**: Sky, Search, Text, Help, Services, Menu, Guide, Info
- **4 UI Pages**: Organized button layout for all functions

### Example on how to use specific channel buttons in activity
<img width="619" height="584" alt="image" src="https://github.com/user-attachments/assets/5c8371bd-7237-4ecd-b006-03aabbe8f77f" />


### Multi-Device Management

When using multiple devices:
- **Independent Control**: Each device operates independently
- **Room-Based Activities**: Create activities for each room/device
- **Centralized Overview**: All devices visible in integration settings
- **Model-Specific**: Automatic device model detection and naming

## Credits

- **Original Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara) — created and maintains the upstream integration that this fork is based on. All architectural credit goes to them; this fork only carries small fixes and quality-of-life changes specific to ES240 use. Please [support their work](https://buymeacoffee.com/meirmiyara) if this integration is useful to you.
- **Upstream Project**: [mase1981/uc-intg-skyq](https://github.com/mase1981/uc-intg-skyq) — the source of this fork
- **SkyQ**: Sky satellite TV platform
- **Unfolded Circle**: Remote 2/3 integration framework (ucapi)
- **pyskyqremote**: Python library for SkyQ control by [Roger Selwyn](https://github.com/RogerSelwyn)
- **Protocol**: SkyQ HTTP API + TCP Remote Control
- **Community**: Testing and feedback from the UC community

## License

This project is licensed under the Mozilla Public License 2.0 (MPL-2.0) - see LICENSE file for details.

## Support & Community

- **Fork Issues** (ES240-specific bugs in this fork): [AshleyFinney/uc-intg-skyq/issues](https://github.com/AshleyFinney/uc-intg-skyq/issues)
- **Upstream Issues** (anything affecting non-ES240 boxes, or general bugs): [mase1981/uc-intg-skyq/issues](https://github.com/mase1981/uc-intg-skyq/issues)
- **UC Community Forum**: [General discussion and support](https://unfolded.community/)
- **Original Developer**: [Meir Miyara](https://www.linkedin.com/in/meirmiyara) — please direct thanks and donations to them, not the fork
- **Sky Support**: [Official Sky Support](https://www.sky.com/help)

---

**Made with ❤️ for the Unfolded Circle and Sky Q communities**

**Original work and ongoing thanks to**: Meir Miyara
