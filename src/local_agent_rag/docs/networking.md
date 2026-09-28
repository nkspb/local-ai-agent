# Networking

## OSI and TCP/IP models

The OSI model describes networking in seven layers: physical, data link, network, transport, session, presentation, and application. In practice, most engineers use the simpler TCP/IP model with four layers: link, internet (IP), transport (TCP/UDP), and application (HTTP, DNS, SSH).

## TCP vs UDP

TCP is connection-oriented. It performs a three-way handshake (SYN, SYN-ACK, ACK), guarantees ordered delivery, and retransmits lost packets. HTTP/1.1, HTTP/2, SSH, and most databases use TCP.

UDP is connectionless. It sends datagrams without a handshake or delivery guarantees, which makes it faster and lighter. DNS queries, video streaming, VoIP, and HTTP/3 (via QUIC) use UDP.

## IP addressing and CIDR

An IPv4 address is 32 bits, written as four octets (for example `192.168.1.10`). CIDR notation adds a prefix length to describe a network: `10.0.0.0/24` contains 256 addresses, from `10.0.0.0` to `10.0.0.255`. A `/16` contains 65,536 addresses.

Private address ranges (RFC 1918) are not routable on the public internet:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

## DNS

DNS translates domain names into IP addresses. A resolver queries root servers, then top-level domain servers, then the authoritative server for the domain, and caches the answer for the record's TTL.

Common record types:

- `A` / `AAAA`: maps a name to an IPv4 / IPv6 address.
- `CNAME`: aliases one name to another name.
- `MX`: specifies mail servers for a domain.
- `TXT`: arbitrary text, often used for domain verification and SPF.
- `NS`: delegates a zone to authoritative name servers.

Use `dig example.com` or `nslookup example.com` to debug resolution.

## Load balancing

A Layer 4 load balancer routes traffic based on IP address and TCP/UDP port without inspecting the payload. A Layer 7 load balancer understands HTTP and can route by host, path, or headers, terminate TLS, and add features like sticky sessions.

Common algorithms are round robin, least connections, and IP hash.

## TLS

TLS encrypts traffic between client and server. During the handshake, the server presents a certificate signed by a certificate authority, the client verifies it, and both sides agree on session keys. TLS 1.3 reduces the handshake to one round trip. In mutual TLS (mTLS), the client also presents a certificate, so both sides authenticate each other.

## Kubernetes networking

Every Pod in a Kubernetes cluster gets its own IP address, and all Pods can reach each other without NAT. A CNI plugin (such as Calico, Cilium, or Flannel) implements this Pod network. kube-proxy programs iptables or IPVS rules on each node so that traffic sent to a Service's virtual IP reaches one of its backing Pods.

NetworkPolicies restrict which Pods may talk to each other. Once a Pod is selected by any NetworkPolicy, all traffic not explicitly allowed by a policy is denied. NetworkPolicies are only enforced if the CNI plugin supports them.

## Troubleshooting tools

- `ping` checks basic reachability using ICMP.
- `traceroute` (or `tracert` on Windows) shows the path packets take.
- `curl -v` shows HTTP request and response details, including the TLS handshake.
- `ss -tulpn` (or `netstat`) lists listening ports and the processes that own them.
- `tcpdump` captures packets for deep inspection.

## Team conventions

These are the internal conventions for our network:

- The office network uses `10.20.0.0/16`; the production VPC uses `10.100.0.0/16`.
- Internal services resolve under the `corp.internal.example` DNS zone.
- All service-to-service traffic in production must use TLS 1.3; TLS 1.2 is allowed only for legacy partners on an approved list.
- Firewall change requests go through the Network team and need approval at least 2 business days in advance.
