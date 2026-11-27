#!/usr/bin/env python3
"""AETHER-264-RS: bounded HTTPS acquisition with pinned public DNS address.

A TLS session and body hash authenticate neither custody nor source ancestry.
"""
import argparse
import base64
import hashlib
import http.client
import ipaddress
import json
import socket
import ssl
import time
from urllib.parse import urlsplit

SCHEMA = "AETHER-264/https-acquisition-v1"
LIMIT = 65536
HOLD = {"operational_authority": "HOLD", "physical_qualification_percent": 0,
        "physical_act_allowed": False, "independent_custody_authenticated": False,
        "independent_source_ancestry_verified": False}

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def public_ip(ip):
    obj = ipaddress.ip_address(ip)
    return obj.is_global and not (obj.is_multicast or obj.is_unspecified)

def validate_url(url, allowed_hosts):
    if not isinstance(url, str) or len(url) > 2048:
        raise ValueError("URL_INVALID")
    part = urlsplit(url)
    if part.scheme != "https" or part.username or part.password or part.fragment:
        raise ValueError("HTTPS_ONLY")
    if part.port not in (None, 443) or not part.hostname:
        raise ValueError("PORT_OR_HOST_INVALID")
    host = part.hostname.lower().rstrip(".")
    if not isinstance(allowed_hosts, (list, tuple, set)) or not allowed_hosts:
        raise ValueError("HOST_ALLOWLIST_REQUIRED")
    if host not in allowed_hosts or not host.isascii() or len(host) > 253:
        raise ValueError("HOST_NOT_ALLOWLISTED")
    # An allowlisted hostname must be a DNS name, never an IP literal.
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("IP_LITERAL_DISALLOWED")
    if any(not label or not label.replace("-", "").isalnum() for label in host.split(".")):
        raise ValueError("HOST_SYNTAX_INVALID")
    return host, (part.path or "/") + ("?" + part.query if part.query else "")

def resolve_public(host):
    addresses = []
    for entry in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM):
        ip = entry[4][0]
        if ip not in addresses:
            addresses.append(ip)
    if not addresses or len(addresses) > 16 or not all(public_ip(x) for x in addresses):
        raise ValueError("DNS_HAS_UNSAFE_OR_NO_ADDRESS")
    return addresses

class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, ip, timeout=3):
        super().__init__(host, port=443, timeout=timeout,
                         context=ssl.create_default_context())
        self.resolved_ip = ip
    def connect(self):
        # Pin the network peer: never let http.client re-resolve the name.
        plain = socket.create_connection((self.resolved_ip, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(plain, server_hostname=self.host)
        except BaseException:
            plain.close()
            raise

def acquire(url, hosts, resolver=resolve_public, factory=PinnedHTTPS):
    host, path = validate_url(url, hosts)
    addresses = resolver(host)
    if not isinstance(addresses, list) or not addresses or len(addresses) > 16:
        raise ValueError("RESOLUTION_INVALID")
    if not all(isinstance(ip, str) and public_ip(ip) for ip in addresses):
        raise ValueError("PRIVATE_OR_RESERVED_DNS_ADDRESS")
    # Pinned first vetted address. An alternative retry never escapes this set.
    ip = addresses[0]
    start = time.monotonic_ns()
    connection = factory(host, ip, timeout=3)
    try:
        connection.request("GET", path, headers={
            "Host": host, "Accept-Encoding": "identity",
            "Connection": "close", "User-Agent": "AETHER-264-RS/1.0"})
        response = connection.getresponse()
        status = response.status
        # A redirect is recorded as a rejection, not silently followed.
        if status not in (200, 206):
            raise ValueError("HTTP_STATUS_NOT_ACCEPTED")
        length = response.getheader("Content-Length")
        if length is not None:
            if not length.isdigit() or int(length) > LIMIT:
                raise ValueError("CONTENT_LENGTH_INVALID")
        if response.getheader("Content-Encoding", "identity").lower() != "identity":
            raise ValueError("COMPRESSED_BODY_DISALLOWED")
        body = response.read(LIMIT + 1)
        if len(body) > LIMIT:
            raise ValueError("BODY_SIZE_LIMIT")
        if length is not None and len(body) != int(length):
            raise ValueError("BODY_TRUNCATED")
        elapsed = (time.monotonic_ns()-start)//1000000
        observation = {"schema": SCHEMA, "requested_url": url, "host": host,
                       "pinned_ip": ip, "dns_address_count": len(addresses),
                       "tls_hostname_validation": True, "status": status,
                       "elapsed_ms": elapsed, "raw_length": len(body),
                       "raw_sha256": sha(body),
                       "raw_b64": base64.b64encode(body).decode("ascii")}
        observation["observation_sha256"] = sha(canonical(observation))
        return {**observation, **HOLD}
    finally:
        connection.close()

def review(doc):
    reasons = []
    required = {"schema","requested_url","host","pinned_ip","dns_address_count",
                "tls_hostname_validation","status","elapsed_ms","raw_length",
                "raw_sha256","raw_b64","observation_sha256"}
    if not isinstance(doc, dict) or not required.issubset(doc):
        return {"verdict":"REJECT_OR_UNVERIFIED","reasons":["OBSERVATION_INVALID"],**HOLD}
    try:
        raw = base64.b64decode(doc["raw_b64"],validate=True)
        if len(raw) > LIMIT or type(doc["raw_length"]) is not int or len(raw) != doc["raw_length"]:
            reasons.append("RAW_LENGTH_INVALID")
        if sha(raw) != doc["raw_sha256"]:
            reasons.append("RAW_DIGEST_INVALID")
        if doc["schema"] != SCHEMA or doc["status"] not in (200,206):
            reasons.append("RECORD_FIELDS_INVALID")
        if not public_ip(doc["pinned_ip"]) or doc["tls_hostname_validation"] is not True:
            reasons.append("NETWORK_PEER_INVALID")
        bare = {k:doc[k] for k in required if k!="observation_sha256"}
        if sha(canonical(bare))!=doc["observation_sha256"]:
            reasons.append("OBSERVATION_DIGEST_MISMATCH")
    except (ValueError,TypeError,KeyError):
        reasons.append("RAW_OR_RECORD_UNDECODABLE")
    reasons.extend(["EXTERNAL_CUSTODY_NOT_AUTHENTICATED",
                    "NETWORK_PEER_NOT_INDEPENDENTLY_OBSERVED",
                    "SOURCE_ANCESTRY_NOT_PROVEN"])
    return {"verdict":"REJECT_OR_UNVERIFIED","reasons":sorted(set(reasons)),**HOLD}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--allow-host", action="append", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()
    try:
        result = acquire(args.url, args.allow_host)
    except (OSError,ValueError,TypeError,ssl.SSLError,socket.timeout) as e:
        result = {"verdict":"REJECT_OR_UNVERIFIED",
                  "reasons":["ACQUISITION_REJECTED:"+type(e).__name__],**HOLD}
    rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.out:
        with open(args.out,"w",encoding="utf-8") as f:
            f.write(rendered)
    print(rendered,end="")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
