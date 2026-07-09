---
name: rustdesk-client
description: >
  Installs and configures the self-hosted RustDesk client on Debian/Ubuntu hosts.
  Downloads the correct architecture-specific .deb package (supporting x86_64 and aarch64),
  resolves all required system dependencies, dynamically configures multi-profile settings
  pointing to the self-hosted rendezvous server, locks down configuration permissions,
  starts and registers the rustdesk service, and returns the machine's unique RustDesk ID.
  Triggers on "install rustdesk client", "setup remote desktop", "configure rustdesk",
  "deploy rustdesk client", "install remote access". Do NOT use for Windows or non-Debian environments.
---

# RustDesk Client Installation Skill

Automated deployment, configuration, and provisioning of the self-hosted RustDesk remote access client on Debian and Ubuntu hosts.

## Overview

This skill automates the end-to-end installation of the RustDesk remote desktop client and binds it directly to a custom self-hosted rendezvous server. It auto-detects hardware architectures (`x86_64` and `aarch64`), configures secure connection parameters (with encrypted connection keys) across all system user profiles—including root, logged-in home users, and graphical display managers—registers the daemon as a systemd service, and fetches the host's unique RustDesk access ID.

## Prerequisites

- Target host operating system must be **Ubuntu** or **Debian**.
- SSH access with sudo privileges on the target node.
- Active network connection to download package files and reach the self-hosted rendezvous server.

## Configuration Details

The installation accepts custom rendezvous settings via parameters or environment variables, which dynamically populates `RustDesk2.toml` across root, home, display manager (GDM, SDDM, LightDM), and volatile GDM greeter paths:
- **Rendezvous Server**: Passed as the first argument or via `$RENDEZVOUS_SERVER`
- **Relay Server**: Passed as the third argument or via `$RELAY_SERVER` (defaults to Rendezvous Server)
- **Public Encryption Key**: Passed as the second argument or via `$PUBLIC_KEY`

## Workflow

### Step 1: Target Architecture Check

The installation starts by running `uname -m` to determine the CPU architecture:
- `x86_64` maps to `rustdesk-1.3.7-x86_64.deb`
- `aarch64` maps to `rustdesk-1.3.7-aarch64.deb`

### Step 2: Download and Install Debian Package

Downloads the appropriate package directly from the official releases repository to `/tmp/`, updates `apt` cache, installs the package alongside required system dependencies, and cleans up the temporary file:

```bash
wget -q "https://github.com/rustdesk/rustdesk/releases/download/1.3.7/${DEB_FILE}" -O "/tmp/${DEB_FILE}"
apt-get update -y && apt-get install -y "/tmp/${DEB_FILE}"
rm -f "/tmp/${DEB_FILE}"
```

### Step 3: Multi-User Profile Configuration

To ensure RustDesk works correctly across all user contexts—including graphical console sessions, logged-in local users, and display manager greeters (such as GDM/GDM3, SDDM, and LightDM)—the installer scans and configures the `RustDesk2.toml` connection profile for all potential user home directories recursively:
1. **Root Profile**: `/root/.config/rustdesk/RustDesk2.toml`
2. **Standard Users**: `/home/*/.config/rustdesk/RustDesk2.toml`
3. **Display Managers**: `/var/lib/gdm3`, `/var/lib/gdm`, etc.
4. **Volatile GDM Sessions**: `/run/gdm3/home/gdm-greeter`, etc.

The script dynamically sets the correct ownership and restricts permission to `600` for each profile to guarantee compatibility and security.

### Step 4: Service Initialization

Reload systemd configurations, enable auto-start, start the service, and pause briefly to allow the client to generate its unique identification hash:

```bash
systemctl daemon-reload
systemctl enable rustdesk
systemctl start rustdesk
sleep 3
```

### Step 5: Unique ID Retrieval

Retrieve the unique generated RustDesk ID from the tool CLI or system options:

```bash
rustdesk --get-id 2>/dev/null || cat /root/.config/rustdesk/RustDesk.toml 2>/dev/null | grep -oP 'id = "\K[^"]+' || echo "unknown"
```

## Inline Installer Script Reference

The unified installer script is embedded below. When using this skill via Tunnel Manager or remote execution commands, copy this script to `/tmp/install_rustdesk_client.sh` and execute it as root:

```bash
#!/bin/bash
set -e

# Ensure running as root
if [ "$EUID" -ne 0 ]; then
  echo "Error: Please run as root or with sudo."
  exit 1
fi

# Accept configurations via environment variables or command-line arguments
RENDEZVOUS_SERVER="${1:-${RENDEZVOUS_SERVER:-}}"
PUBLIC_KEY="${2:-${PUBLIC_KEY:-}}"
RELAY_SERVER="${3:-${RELAY_SERVER:-$RENDEZVOUS_SERVER}}"

if [ -z "$RENDEZVOUS_SERVER" ] || [ -z "$PUBLIC_KEY" ]; then
  echo "Error: RENDEZVOUS_SERVER and PUBLIC_KEY must be provided as arguments or environment variables."
  echo "Usage: $0 <rendezvous_server> <public_key> [relay_server]"
  exit 1
fi

VERSION="1.3.7"
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
  DEB_FILE="rustdesk-${VERSION}-x86_64.deb"
elif [ "$ARCH" = "aarch64" ]; then
  DEB_FILE="rustdesk-${VERSION}-aarch64.deb"
else
  echo "Error: Unsupported architecture: $ARCH"
  exit 1
fi

echo "Detected architecture: $ARCH. Preparing to install $DEB_FILE..."

# Stop service if already running
if systemctl is-active --quiet rustdesk; then
  echo "Stopping active rustdesk service..."
  systemctl stop rustdesk || true
fi

# Download package
echo "Downloading RustDesk \$VERSION package..."
wget -q "https://github.com/rustdesk/rustdesk/releases/download/\${VERSION}/\${DEB_FILE}" -O "/tmp/\${DEB_FILE}"

# Install package and dependencies
echo "Installing package and resolving system dependencies..."
apt-get update -y
apt-get install -y "/tmp/\${DEB_FILE}"

# Cleanup temporary package file
rm -f "/tmp/\${DEB_FILE}"

# Configure RustDesk client settings
echo "Configuring self-hosted server settings..."

# Define configuration content dynamically
CONFIG_CONTENT="rendezvous_server = '\${RENDEZVOUS_SERVER}'

[options]
custom-rendezvous-server = '\${RENDEZVOUS_SERVER}'
key = '\${PUBLIC_KEY}'
relay-server = '\${RELAY_SERVER}'
"

# Function to write and secure configuration for a home directory
configure_user_dir() {
  local home_dir="\$1"
  local owner_user="\$2"
  local owner_group="\$3"

  if [ -d "\$home_dir" ]; then
    local config_dir="\${home_dir}/.config/rustdesk"
    echo "Configuring RustDesk for user '\$owner_user' at: \$config_dir"

    # Create directories
    mkdir -p "\$config_dir"

    # Write configuration
    echo "\$CONFIG_CONTENT" > "\${config_dir}/RustDesk2.toml"

    # Set correct permissions
    chmod 600 "\${config_dir}/RustDesk2.toml"

    # Set ownership recursively if owner is provided, otherwise detect
    if [ -n "\$owner_user" ] && [ -n "\$owner_group" ]; then
      chown -R "\${owner_user}:\${owner_group}" "\${home_dir}/.config" 2>/dev/null || true
    else
      local detected_owner=\$(stat -c "%U:%G" "\$home_dir" 2>/dev/null || echo "root:root")
      chown -R "\$detected_owner" "\${home_dir}/.config" 2>/dev/null || true
    fi
  fi
}

# 1. Configure Root Profile
configure_user_dir "/root" "root" "root"

# 2. Configure Standard User Profiles under /home
for user_home in /home/*; do
  if [ -d "\$user_home" ]; then
    user_name=\$(basename "\$user_home")
    # Skip standard special directories if any
    if [ "\$user_name" != "lost+found" ]; then
      user_group=\$(stat -c "%G" "\$user_home" 2>/dev/null || echo "\$user_name")
      configure_user_dir "\$user_home" "\$user_name" "\$user_group"
    fi
  fi
done

# 3. Configure Display Manager Users (GDM, GDM3, SDDM, LightDM)
DM_USERS=("gdm-greeter" "gdm" "gdm3" "lightdm" "sddm")
for u in "\${DM_USERS[@]}"; do
  if id "\$u" &>/dev/null; then
    passwd_home=\$(getent passwd "\$u" | cut -d: -f6)
    u_group=\$(id -gn "\$u" 2>/dev/null || echo "\$u")
    if [ -n "\$passwd_home" ] && [ -d "\$passwd_home" ]; then
      configure_user_dir "\$passwd_home" "\$u" "\$u_group"
    fi
  fi
done

# 4. Explicitly handle volatile GDM greeter paths commonly found on Debian/Ubuntu
VOLATILE_GDM_PATHS=(
  "/run/gdm3/home/gdm-greeter"
  "/var/lib/gdm3"
  "/var/lib/gdm"
)
for volatile_path in "\${VOLATILE_GDM_PATHS[@]}"; do
  if [ -d "\$volatile_path" ]; then
    # Detect running owner/group for this path or fallback to gdm-greeter:gdm or gdm:gdm
    path_owner=\$(stat -c "%U" "\$volatile_path" 2>/dev/null || echo "")
    path_group=\$(stat -c "%G" "\$volatile_path" 2>/dev/null || echo "")

    if [ -n "\$path_owner" ] && [ -n "\$path_group" ]; then
      configure_user_dir "\$volatile_path" "\$path_owner" "\$path_group"
    fi
  fi
done

# Start and enable system service
echo "Starting and enabling rustdesk systemd service..."
systemctl daemon-reload
systemctl enable rustdesk
systemctl start rustdesk

# Wait for service initialization to populate the local ID
sleep 3

# Retrieve unique RustDesk ID
RUSTDESK_ID=\$(rustdesk --get-id 2>/dev/null || cat /root/.config/rustdesk/RustDesk.toml 2>/dev/null | grep -oP 'id = "\K[^"]+' || echo "unknown")
echo "RUSTDESK_ID_RESULT:\$RUSTDESK_ID"
```

## Troubleshooting & Verification

- **Service Status**: Check with `systemctl status rustdesk` to confirm it is active.
- **Rendezvous Logs**: If the client cannot connect, verify network connectivity to the self-hosted rendezvous server by running `ping <your_rendezvous_server>`.
- **Config Override**: Verify configuration contents match the expected key signature.
- **Split-Brain DNS / LAN Resolution Mismatch**:
  - **Symptom**: Client logs "Connection Error, ID does not exist". Pinging the rendezvous domain (e.g., `rustdesk.example.com`) on an internal node resolves to a public WAN IP rather than the local IP (e.g., `10.0.0.10`), meaning hbbs/hbbr ports are unreachable.
  - **Diagnosis**: The host's resolver/link config bypasses the local DNS (e.g., local DNS server at `10.0.0.100`) in favor of external providers like `1.1.1.1`.
  - **Remediation**: Add a static hostname entry to `/etc/hosts` to force the correct internal routing:
    ```bash
    echo "10.0.0.10 rustdesk.example.com" | sudo tee -a /etc/hosts
    ```
- **Wayland "Please select the screen to be shared" / Greeter Session Hangs**:
  - **Symptom**: Connecting to a Linux client triggers a modal popup reading *"Please select the screen to be shared (Operate on the peer side)"*, which hangs unattended connections indefinitely. On GDM login screens, the remote screen remains blank or refuses connection.
  - **Diagnosis**: Wayland isolates desktop sessions and greeters, requiring interactive user consent to share screens. RustDesk requires an X11-native session to access the framebuffer unattended.
  - **Remediation on Ubuntu 24.04 and older (GDM < 50.0)**:
    Force GDM to use X11 (Xorg) by editing `/etc/gdm3/custom.conf` and uncommenting/adding `WaylandEnable=false` under the `[daemon]` block:
    ```bash
    # Force X11 / Disable Wayland
    sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf
    # Restart display manager to apply changes
    sudo systemctl restart gdm3
    ```
  - **Remediation on Ubuntu 26.04+ (GNOME 50 / GDM 50.0+)**:
    GNOME 50.0 has **fully deprecated and removed X11 backend support from GDM**. Modifying `/etc/gdm3/custom.conf` has NO effect on the login greeter, which always starts in Wayland mode. To solve this, you must migrate the display manager to **LightDM** (which supports X11 greeters):
    1. Pre-seed debconf to select LightDM as default and install it non-interactively:
       ```bash
       echo "shared/default-x-display-manager select lightdm" | sudo debconf-set-selections
       sudo DEBIAN_FRONTEND=noninteractive apt-get install -y lightdm lightdm-gtk-greeter
       ```
    2. Write the default display manager path:
       ```bash
       echo "/usr/sbin/lightdm" | sudo tee /etc/X11/default-display-manager
       ```
    3. Disable GDM3 and enable LightDM:
       ```bash
       sudo systemctl disable gdm3
       sudo systemctl enable lightdm
       # Or force symlink update:
       sudo ln -sf /lib/systemd/system/lightdm.service /etc/systemd/system/display-manager.service
       ```
    4. Stop GDM3 and start LightDM to apply:
       ```bash
       sudo systemctl stop gdm3
       sudo systemctl start lightdm
       ```
    5. **Force User Session to X11 (Prevent Post-Login Wayland Redirect)**:
       * **Symptom**: After migrating GDM to LightDM, the login screen successfully displays via X11. However, immediately after logging in, the desktop redirects to a Wayland session, triggering the *"Wayland Please select the screen to be shared"* popup.
       * **Cause**: The logged-in user's desktop session config in AccountsService still defaults to Wayland (`Session=ubuntu`). LightDM respects this and launches GNOME on Wayland.
       * **Remediation**: We must force both the global LightDM session and the per-user desktop session config to `ubuntu-xorg` (X11):
         * **Global LightDM Default**: Create a drop-in configuration file `/etc/lightdm/lightdm.conf.d/50-default-xorg.conf`:
           ```ini
           [Seat:*]
           user-session=ubuntu-xorg
           ```
           Apply this via shell:
           ```bash
           echo -e "[Seat:*]\nuser-session=ubuntu-xorg" | sudo tee /etc/lightdm/lightdm.conf.d/50-default-xorg.conf
           ```
         * **Per-User Configuration**: Update the AccountsService user definition for the remote user (e.g., `<username>` = `genius`):
           ```bash
           # Update or insert Session and XSession keys in /var/lib/AccountsService/users/<username>
           sudo python3 -c "import sys; filepath='/var/lib/AccountsService/users/genius'; f=open(filepath,'r'); content=f.read(); f.close(); lines=content.splitlines(); out=[]; [out.append('Session=ubuntu-xorg') if l.startswith('Session=') else (out.append('XSession=ubuntu-xorg') if l.startswith('XSession=') else out.append(l)) for l in lines]; [out.insert(out.index('[User]')+1, 'XSession=ubuntu-xorg') if not any(x.startswith('XSession=') for x in out) else None]; [out.insert(out.index('[User]')+1, 'Session=ubuntu-xorg') if not any(x.startswith('Session=') for x in out) else None]; f=open(filepath,'w'); f.write('\n'.join(out)+'\n'); f.close()"
           ```
         * **Restart Display Manager to Apply**:
           ```bash
           sudo systemctl restart lightdm
           ```
    6. Verify the active session type is X11:
       ```bash
       loginctl list-sessions --no-legend | awk '{print $1}' | while read id; do loginctl show-session "$id" -p Type; done
       # Output should be Type=x11 for seat0 (login/greeter session) and Type=x11 for user desktop sessions
       ```
