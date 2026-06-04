---
name: ipmi-bmc-manager
description: >
  IPMI / BMC management atomic skill. Controls server power, opens Serial-over-LAN consoles,
  reads sensors and event logs, and configures the BMC LAN on out-of-band controllers
  (Dell iDRAC, HPE iLO, Supermicro, generic IPMI 2.0) via ipmitool — in-band or over LAN.
  Use for remote power control and for recovering a node whose OS network is unreachable.
domain: infrastructure
tags:
  - ipmi
  - idrac
  - bmc
  - out-of-band
  - recovery
  - power
  - serial-over-lan
requires:
  - ipmitool
  - systems-manager-mcp   # optional: to run ipmitool on remote hosts via SSH
---

# IPMI / BMC Manager Skill

Stateless atomic operations against a server's **baseboard management controller** (BMC) — the
always-on management processor (Dell **iDRAC**, HPE **iLO**, Supermicro, or generic **IPMI 2.0**).
The BMC is independent of the host OS: it answers even when the OS is down or the machine is
powered off (as long as it has standby power). This makes it the reliable path for **remote
power control** and **out-of-band recovery** after a change locks you out of SSH (bad netplan,
firewall, kernel panic).

## Prerequisites
- `ipmitool` on the controlling host (`apt-get install -y ipmitool`). It loads `ipmi_si` +
  `ipmi_devintf` and creates `/dev/ipmi0` for in-band access.
- Access path (one of):
  - **In-band** — running on the target's own OS: `sudo ipmitool <cmd>` (no IP/creds; talks to
    the local BMC over the KCS interface at `/dev/ipmi0`).
  - **Out-of-band** — over the network to the BMC's IP: `ipmitool -I lanplus -H <BMC_IP> -U <user> -P <pw> <cmd>`.
- `systems-manager-mcp` (optional) to execute `ipmitool` on remote hosts over SSH when you
  don't have a session on the target.

> Never hardcode BMC passwords in scripts/commits. Read from an env/secret. Default Dell iDRAC
> creds are `root`/`calvin` — assume they should be rotated.

## Operations

### 1. Discover / verify the BMC
```bash
sudo ipmitool mc info                 # vendor, firmware, IPMI version
sudo ipmitool lan print 1             # BMC network config on channel 1 (often 1; iLO may use 2)
ls /dev/ipmi*                          # in-band device present?
```
Capture: manufacturer (Dell/HPE/Supermicro), firmware, BMC IP, IP source (static/dhcp), channel.

### 2. Power & chassis control
```bash
ipmitool ... chassis status           # current power state
ipmitool ... power status
ipmitool ... power on | off | cycle | reset | soft
ipmitool ... chassis identify 30      # blink the locator LED 30s
ipmitool ... chassis bootdev pxe|disk|bios   # one-time next-boot device
```
Prefer `power cycle`/`reset` over `off` for recovery (avoids leaving a node down).

### 3. Sensors, health, event log
```bash
ipmitool ... sensor list              # all sensors (temp/fan/voltage/power)
ipmitool ... sdr type Temperature
ipmitool ... sdr type Fan
ipmitool ... sel list                 # system event log (faults, power events)
ipmitool ... sel elist | tail -20
ipmitool ... sel clear                # after reviewing
```

### 4. Serial-over-LAN console (recovery)
The OS must emit its console to the BMC serial port (kernel cmdline e.g. `console=ttyS1,115200n8`
for Dell iDRAC; verify the right ttyS for the platform).
```bash
ipmitool ... sol info 1               # SoL config
ipmitool -I lanplus -H <BMC_IP> -U <u> -P <pw> sol activate    # exit with: ~ then .
ipmitool ... sol deactivate           # if a stale session is stuck
```

### 5. Configure the BMC LAN from the OS (no BIOS reboot)
Use this to bring an unconfigured/off-subnet BMC onto the management network — do it BEFORE any
risky network change so recovery is possible.
```bash
sudo ipmitool lan set 1 ipsrc static
sudo ipmitool lan set 1 ipaddr   <BMC_IP>
sudo ipmitool lan set 1 netmask  <MASK>
sudo ipmitool lan set 1 defgw ipaddr <GW>
sudo ipmitool lan set 1 access on
sudo ipmitool lan set 1 auth ADMIN MD5
sudo ipmitool mc reset cold          # reboots the BMC ONLY (not the server) to apply
```

### 6. BMC user management
```bash
ipmitool ... user list 1
sudo ipmitool user set name 2 <user>
sudo ipmitool user set password 2
sudo ipmitool user enable 2
sudo ipmitool channel setaccess 1 2 callin=on ipmi=on link=on privilege=4   # admin
```

## Recovery workflow (node unreachable after a network/host change)
1. From any reachable host: `ipmitool -I lanplus -H <BMC_IP> -U <u> -P <pw> power status`.
2. `... sol activate` → log in on the serial console → fix the config (revert netplan, restart
   networking) → confirm connectivity returns.
3. If the OS is wedged: `... power cycle`, then re-attach SoL to watch it boot.

## Safety & boundaries
- **`power off`/`cycle` are disruptive** — confirm the target host before issuing; never script
  a fleet-wide power action without explicit intent.
- `mc reset cold` reboots the **BMC**, not the server (safe; momentarily drops BMC access).
- Vendor quirks: HPE iLO is usually LAN channel **2**; Supermicro often needs `-I lanplus`;
  some BMCs need `lan set 1 cipher_privs ...` for `lanplus`. If `lan print` is empty, try the
  other channel.
- Out-of-band needs the BMC's dedicated/shared NIC connected and on a reachable subnet.

## Notes
- In-band works with zero credentials/network — ideal for first discovery and for configuring
  the LAN. Out-of-band is what survives an OS/network outage.
- Pair with `host-resource-sampler` (OS metrics) for full health; BMC sensors cover hardware
  (temps/fans/PSU) the OS can't always see.

See `references/cheatsheet.md` for a copy-paste command reference. Homelab-specific iDRAC
addresses live in the inventory repo (`inventory/IPMI.md`).
