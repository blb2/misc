#!/usr/bin/env python3


from datetime import datetime
import ipaddress
import json
import subprocess
import sys
import urllib.request


# DigitalOcean API v2: https://docs.digitalocean.com/reference/api/api-reference/
DO_DOMAIN  = ""
DO_NAME    = ""
DO_TOKEN   = ""
IPV4_URL   = ""
IPV6_URL   = ""
IPV6_ULA   = "::/128"
IPV6_CMD   = "ip -6 addr show dev eth0 scope global primary | fgrep inet6 | cut -d ' ' -f 6 | cut -d '/' -f 1"


def logmsg(msg):
    print(f"[{datetime.now()}] {msg}")


def logerr(err):
    print("[{datetime.now()}] {msg}", file=sys.stderr)


def get_ip(record_type):
    if record_type == "AAAA":
        # TODO: It would be cooler to query IPV6_URL, but I need to find a way to specify a non-temporary
        # network interface.
        ula_prefix = ipaddress.ip_network(IPV6_ULA)
        try:
            ret = subprocess.run(IPV6_CMD, shell=True, universal_newlines=True, stdout=subprocess.PIPE)
            if ret.returncode == 0 and ret.stdout:
                for line in ret.stdout.split('\n'):
                    try:
                        ip = ipaddress.ip_address(line)
                        if ip not in ula_prefix:
                            return str(ip)
                    except ValueError as e:
                        pass
        except Exception as e:
            logerr("Exception attempting to obtain IPv6 address")
        return None
    elif record_type == "A":
        url = IPV4_URL
    else:
        return None
    if not url:
        return None
    # If IPV4_URL is the same as IPV6_URL, it would be very cool to specify forcing IPv4 or IPv6 when making
    # the request.
    request = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(request) as f:
            if f.status == 200 and "text/plain" in f.getheader("Content-Type", ""):
                return f.read().decode("utf-8").rstrip()
    except urllib.error.URLError as e:
        logerr(f"Exception while requesting public IP: {e.reason}")
    except Exception as e:
        logerr(f"Unknown exception while requesting public IP: {e}")
    return None


def get_dns_records(domain, name, token):
    url     = f"https://api.digitalocean.com/v2/domains/{domain}/records?per_page=200"
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {token}" }
    records = {}
    while url:
        request = urllib.request.Request(url=url, headers=headers, method="GET")
        url = None
        try:
            with urllib.request.urlopen(request) as f:
                if f.status == 200 and "application/json" in f.getheader("Content-Type", ""):
                    try:
                        doc = json.load(f)
                        if "domain_records" in doc:
                            for record in doc["domain_records"]:
                                if record["name"] == name:
                                    records[record["type"]] = record
                        url = doc["links"]["pages"]["next"]
                    except json.JSONDecodeError as e:
                        logerr(f"Exception decoding JSON from DNS records: {e}")
                    except KeyError as e:
                        pass
        except urllib.error.URLError as e:
            logerr(f"Exception while requesting DNS records: {e.reason}")
        except Exception as e:
            logerr(f"Unknown exception while requesting DNS records: {e}")
    return records


def set_dns_record(domain, token, record_id, record_type, record_data):
    url     = f"https://api.digitalocean.com/v2/domains/{domain}/records/{record_id}"
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {token}" }
    data    = json.JSONEncoder().encode({ "data": record_data }).encode("utf-8")
    request = urllib.request.Request(url=url, headers=headers, data=data, method="PUT")
    try:
        with urllib.request.urlopen(request) as f:
            if f.status == 200 and "application/json" in f.getheader("Content-Type", ""):
                logmsg(f"Successfully updated {record_type} record to {record_data}")
    except urllib.error.URLError as e:
        logerr(f"Exception while updating {record_type} record: {e.reason}")
    except Exception as e:
        logerr(f"Unknown exception while updating {record_type} record: {e}")


def update_dns_record(domain, token, records, record_type):
    if record_type not in records:
        logerr(f"Could not locate {record_type} record")
        return
    if "id" not in records[record_type]:
        logerr(f"Could not locate ID in {record_type} record")
        return
    if "data" not in records[record_type]:
        logerr(f"Could not locate data in {record_type} record")
        return
    ip = get_ip(record_type)
    if not ip:
        logerr(f"Could not get public IP for updating {record_type} record")
        return
    if ip != records[record_type]["data"]:
        set_dns_record(domain, token, records[record_type]["id"], record_type, ip)
    else:
        logmsg(f"No IP change detected for {record_type} record with IP {ip}")


def update_dns(domain, name, token):
    logmsg("Beginning DNS update...")
    records = get_dns_records(domain, name, token)
    if records:
        update_dns_record(domain, token, records, "A")
        update_dns_record(domain, token, records, "AAAA")
    else:
        logerr(f"Could not retrieve domain records for {domain} ({name})")
    logmsg("OK")


if __name__ == "__main__":
    if not DO_TOKEN:
        sys.exit("DigitalOcean API token (DO_TOKEN) not specified")
    if not DO_DOMAIN:
        sys.exit("DigitalOcean domain (DO_DOMAIN) not specified")
    if not DO_NAME:
        sys.exit("DigitalOcean subdomain (DO_NAME) not specified")
    update_dns(DO_DOMAIN, DO_NAME, DO_TOKEN)
