# ipmitool cheat sheet

`IB` = in-band (`sudo ipmitool …` on the target). `OOB` = out-of-band
(`ipmitool -I lanplus -H <BMC_IP> -U <user> -P <pw> …` from anywhere).

## Install
```bash
sudo apt-get install -y ipmitool      # Debian/Ubuntu
sudo dnf install -y ipmitool          # RHEL/Fedora
ls /dev/ipmi0                          # in-band device (else: modprobe ipmi_si ipmi_devintf)
```

## Discovery
| Action | Command |
|---|---|
| BMC info | `ipmitool mc info` |
| LAN config (ch.1) | `ipmitool lan print 1` |
| Find the right channel | `for c in 1 2 3; do ipmitool lan print $c 2>/dev/null && echo "ch=$c"; done` |
| Self test | `ipmitool mc selftest` |

## Power / chassis
| Action | Command |
|---|---|
| State | `ipmitool chassis status` / `ipmitool power status` |
| On / Off | `ipmitool power on` / `ipmitool power off` |
| Cycle / Reset | `ipmitool power cycle` / `ipmitool power reset` |
| Graceful shutdown | `ipmitool power soft` |
| Locator LED | `ipmitool chassis identify 30` |
| One-time boot dev | `ipmitool chassis bootdev pxe options=efiboot` |

## Sensors / logs
| Action | Command |
|---|---|
| All sensors | `ipmitool sensor list` |
| Temps / Fans | `ipmitool sdr type Temperature` / `ipmitool sdr type Fan` |
| Event log | `ipmitool sel list` / `ipmitool sel elist` |
| Clear log | `ipmitool sel clear` |

## Serial-over-LAN
| Action | Command |
|---|---|
| Info | `ipmitool sol info 1` |
| Connect (OOB) | `ipmitool -I lanplus -H <IP> -U <u> -P <pw> sol activate` — exit: `~` then `.` |
| Kill stale session | `ipmitool sol deactivate` |
| Kernel cmdline (Dell) | `console=ttyS1,115200n8` (HPE often `ttyS0`) |

## Configure BMC LAN (from OS, in-band)
```bash
ipmitool lan set 1 ipsrc static
ipmitool lan set 1 ipaddr 10.0.0.110
ipmitool lan set 1 netmask 255.0.0.0
ipmitool lan set 1 defgw ipaddr 10.0.0.1
ipmitool lan set 1 access on
ipmitool lan set 1 auth ADMIN MD5
ipmitool lan set 1 cipher_privs XaaaXXaaaXXaaXX   # if lanplus auth fails
ipmitool mc reset cold                             # apply (reboots BMC only)
```

## Users
```bash
ipmitool user list 1
ipmitool user set name 2 admin
ipmitool user set password 2
ipmitool user enable 2
ipmitool channel setaccess 1 2 callin=on ipmi=on link=on privilege=4
```

## Vendor notes
- **Dell iDRAC:** LAN channel 1; default `root`/`calvin`; SoL on `ttyS1`. iDRAC6/7 (R510/R710/R820)
  text SoL is free; graphical KVM needs Enterprise license.
- **HPE iLO:** LAN channel **2**; SoL on `ttyS0`.
- **Supermicro:** always use `-I lanplus`; default `ADMIN`/`ADMIN`.

## Out-of-band one-liner
```bash
IPMI="ipmitool -I lanplus -H 10.0.0.113 -U root -P $IDRAC_PW"
$IPMI power status && $IPMI sel elist | tail -10
```
