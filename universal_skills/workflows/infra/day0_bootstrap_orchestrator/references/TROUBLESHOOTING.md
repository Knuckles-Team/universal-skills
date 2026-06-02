# Day-0 / Swarm Troubleshooting Runbook

Hard-won runbook from real incidents recovering the Heaven Homestead swarm. Symptom →
diagnosis → fix. Topology: manager **R820 (10.0.0.13)**; workers R510(.10) R710(.11)
RW710(.12) GR1080(.16) GB10(.18); DNS = Technitium macvlan **10.0.0.199**; ingress = Caddy
on R820 (host-mode 80/443); ~76 stacks, GitOps-bound to `http://gitlab.arpa`.

> Access notes: passwordless `sudo` works on **R820 only** (NOT R710/R510 — those need the
> operator). Drive everything over the **tunnel-manager MCP** (`tun__tm_remote run_command`,
> host=IP, user=genius, id_file=~/.ssh/id_rsa) — always pass a short `timeout`. During any DNS
> outage, the Portainer/Caddy/Technitium MCPs (which target `*.arpa`) go dark; only tunnel-manager
> (IP-based) survives.

---

## 1. Swarm reports "no leader" / quorum lost

**Symptom:** `docker node ls` → `rpc error: ... swarm does not have a leader`.
**Diagnose:** `docker info | grep -A3 'Manager Addresses'` and `docker node inspect self --format '{{.ManagerStatus.Addr}}'`. Check whether a listed manager IP still exists: `ip -4 addr show | grep <ip>`.
**Root cause seen:** the manager (R820) was renumbered (`.136`→`.13`); raft still advertised the dead `.136`, so quorum couldn't form.
**Fix (surgical, keeps services running):**
```bash
# On the surviving manager ONLY (never two nodes):
docker swarm init --force-new-cluster --advertise-addr 10.0.0.13
```
This restores a single-manager leader with all services intact.

## 2. force-new-cluster did NOT change the advertise address

**Symptom:** after force-new-cluster, `docker node inspect self --format '{{.ManagerStatus.Addr}}'` still shows the OLD/dead IP; workers can't reconnect (stay `Down`); `docker info` on a worker shows `Manager Addresses: <dead ip>`.
**Cause:** Docker cannot rebind a manager's advertise-addr in place; force-new-cluster preserves it.
**Fixes:**
- **Zero-downtime:** re-add the old IP as an alias so the advertised address resolves to the manager again:
  ```bash
  sudo ip addr add 10.0.0.136/8 dev eno1   # NOT reboot-persistent — persist via netplan/systemd
  ```
- **Clean (downtime):** full swarm re-init with `--advertise-addr 10.0.0.13` (only way to truly drop the old IP).

## 3. Workers `Down` after a manager change

**Fix:** on each worker, `docker swarm leave --force` then rejoin with a FRESH token:
```bash
# manager: docker swarm join-token -q worker   (token rotates on re-init!)
docker swarm leave --force; sleep 3
docker swarm join --token <FRESH> 10.0.0.13:2377
```
Workers connect via the listen addr (`0.0.0.0:2377`), so `10.0.0.13:2377` works even if the advertise addr is wrong. After rejoin, remove stale `Down` duplicates and relabel:
```bash
docker node ls --format '{{.ID}}|{{.Status}}' | awk -F'|' '$2=="Down"{print $1}' | xargs -r docker node rm --force
for n in $(docker node ls --format '{{.Hostname}}'); do docker node update --label-add name=$n $n; done
```

## 4. `*.arpa` resolves to a dead IP

**Diagnose:** `td__zones export_zone` (zone=arpa). Look for the **wildcard `*`** record and explicit overrides.
**Fix:** repoint via `td__zones update_record` (params: domain, zone, type=A, ipAddress=OLD, newIpAddress=NEW). The wildcard `*.arpa` covers every name without an explicit record — fixing it fixes most services at once.

---

## 5. ⚠️ DO NOT do an in-place `caddy` overlay subnet change on a live swarm

**This caused a multi-hour partial outage. Change shared-overlay subnets ONLY via a fresh network on a re-init/maintenance window — never by mass detach/reattach of a live network.**

**What happens if you try** (`docker service update --network-rm/--network-add` across all attached services):
- `docker network rm caddy` **fails** ("has active endpoints") even after the manager shows 0 endpoints — a swarm stale-endpoint race across nodes; retries don't help.
- The mass detach/reattach **corrupts the overlay's service-VIP load-balancer (IPVS) state**: ~N services end up running-but-unreachable via Caddy (502).

**The 502 signature (and how to tell it's the LB/VIP, not the app or the network):**
```bash
CC=$(docker ps --format '{{.Names}}' | grep -i caddy | head -1)
docker exec $CC ping -c2 <svc_vip>        # L3 works (0% loss)  → overlay routing OK
docker exec $CC wget -S -O /dev/null http://<svc_vip>:<port>/   # TCP to VIP TIMES OUT
# On the backend's node: app is healthy locally:
docker exec <task> wget -qO- -S http://127.0.0.1:<port>/        # HTTP/1.1 200 OK
cat /sys/class/net/eth*/mtu                                     # caddy iface MTU == network MTU (rule out MTU)
```
App healthy + ping OK + TCP-to-VIP times out + MTU correct = **stale overlay VIP/IPVS state**.

**What does NOT fix it** (all tried and failed): Caddy restart; `docker service update --force <svc>`; docker restart on the manager AND backend nodes; node leave/rejoin + relabel; per-service serial `--network-rm`/`--network-add`.

**What DOES fix it (deterministic):**
- **Recreate the `caddy` network fresh** — clears all VIP/IPVS state. Requires `docker network rm caddy` to succeed (only reliable after all attached services are gone, e.g. during a stack-wide redeploy or swarm re-init).
- **Swarm teardown + re-init** + GitOps redeploy (guaranteed; biggest outage).

**Prereq before any teardown:** verify the GitOps redeploy path works FIRST — 73/76 stacks redeploy from `http://gitlab.arpa` with auth. If Portainer git-redeploy errors (500), a teardown is unrecoverable. Confirm `gitlab.arpa` git endpoint reachable: `curl -s -o /dev/null -w '%{http_code}' -L http://gitlab.arpa/<group>/<repo>.git/info/refs?service=git-upload-pack` → expect `401` (reachable, needs auth).

---

## 6. Caddy ingress reachability quick test
```bash
for h in portainer gitlab grafana <svc>; do
  printf "%-14s " "$h.arpa"
  curl -s -m6 -o /dev/null -w "%{http_code}\n" -H "Host: $h.arpa" http://10.0.0.13/
done   # 2xx/3xx/401/403 = reachable; 502 = Caddy up but upstream unreachable; 000 = ingress down
```

## 7. tunnel-manager MCP
Always pass a short `timeout` (e.g. 10). The hardened client (bounded connect/banner/auth
timeouts, retry+backoff, keepalive, bounded exit-status) fails fast on dead hosts instead of hanging.
