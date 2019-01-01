#!/usr/bin/env python3


import ipaddress
import json
import subprocess
import sys
import urllib.request


# DigitalOcean API v2: https://developers.digitalocean.com/documentation/v2/
DO_DOMAIN  = ""
DO_NAME    = ""
DO_TOKEN   = ""
IPV4_URL   = ""
IPV6_URL   = ""
IPV6_ULA   = "fdeb:eeb:e20c::/48"
IPV6_CMD   = "ip -6 addr show dev eth0 scope global primary | grep inet6 | cut -d ' ' -f 6 | cut -d '/' -f 1"


def get_ip(record_type):
    if record_type == "AAAA":
        # TODO: It would be cooler to query IPV6_URL, but I need to find a way
        # to specify a non-temporary network interface.
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
            print("Exception attempting to obtain IPv6 address", file=sys.stderr)
        return None
    elif record_type == "A":
        url = IPV4_URL
    else:
        return None
    if not url:
        return None
    # If IPV4_URL is the same as IPV6_URL, it would be very cool to specify
    # forcing IPv4 or IPv6 when making the request.
    request = urllib.request.Request(url=url, method="GET")
    try:
        with urllib.request.urlopen(request) as f:
            if f.status == 200 and "text/plain" in f.getheader("Content-Type", ""):
                return f.read().decode("utf-8").rstrip()
    except urllib.error.URLError as e:
        print("Exception while requesting public IP: {}".format(e.reason), file=sys.stderr)
    except Exception as e:
        print("Unknown exception while requesting public IP: {}".format(e), file=sys.stderr)
    return None


def get_dns_records(domain, name, token):
    url     = "https://api.digitalocean.com/v2/domains/{}/records?per_page=200".format(domain)
    headers = { "Content-Type": "application/json", "Authorization": "Bearer {}".format(token) }
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
                        print("Exception decoding JSON from DNS records: {}".format(e))
                    except KeyError as e:
                        pass
        except urllib.error.URLError as e:
            print("Exception while requesting DNS records: {}".format(e.reason), file=sys.stderr)
        except Exception as e:
            print("Unknown exception while requesting DNS records: {}".format(e), file=sys.stderr)
    return records


def set_dns_record(domain, token, record_id, record_type, record_data):
    url     = "https://api.digitalocean.com/v2/domains/{}/records/{}".format(domain, record_id)
    headers = { "Content-Type": "application/json", "Authorization": "Bearer {}".format(token) }
    data    = json.JSONEncoder().encode({ "data": record_data }).encode("utf-8")
    request = urllib.request.Request(url=url, headers=headers, data=data, method="PUT")
    try:
        with urllib.request.urlopen(request) as f:
            if f.status == 200 and "application/json" in f.getheader("Content-Type", ""):
                print("Successfully updated {} record to {}".format(record_type, record_data))
    except urllib.error.URLError as e:
        print("Exception while updating {} record: {}".format(record_type, e.reason), file=sys.stderr)
    except Exception as e:
        print("Unknown exception while updating {} record: {}".format(record_type, e), file=sys.stderr)


def update_dns_record(domain, token, records, record_type):
    if record_type not in records:
        print("Could not locate {} record".format(record_type), file=sys.stderr)
        return
    if "id" not in records[record_type]:
        print("Could not locate ID in {} record".format(record_type), file=sys.stderr)
        return
    if "data" not in records[record_type]:
        print("Could not locate data in {} record".format(record_type), file=sys.stderr)
        return
    ip = get_ip(record_type)
    if not ip:
        print("Could not get public IP for updating {} record".format(record_type), file=sys.stderr)
        return
    if ip != records[record_type]["data"]:
        set_dns_record(domain, token, records[record_type]["id"], record_type, ip)
    else:
        print("No IP change detected for {} record with IP {}".format(record_type, ip))


def update_dns(domain, name, token):
    records = get_dns_records(domain, name, token)
    if records:
        update_dns_record(domain, token, records, "A")
        update_dns_record(domain, token, records, "AAAA")
    else:
        print("Could not retrieve domain records for {} ({})".format(domain, name), file=sys.stderr)


if __name__ == "__main__":
    if not DO_TOKEN:
        sys.exit("DigitalOcean API token (DO_TOKEN) not specified")
    if not DO_DOMAIN:
        sys.exit("DigitalOcean domain (DO_DOMAIN) not specified")
    if not DO_NAME:
        sys.exit("DigitalOcean subdomain (DO_NAME) not specified")
    update_dns(DO_DOMAIN, DO_NAME, DO_TOKEN)
