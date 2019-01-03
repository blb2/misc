#!/usr/bin/env python3


from datetime import datetime
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
IPV6_ULA   = "::/128"
IPV6_CMD   = "ip -6 addr show dev eth0 scope global primary | grep inet6 | cut -d ' ' -f 6 | cut -d '/' -f 1"


def logmsg(msg):
    print("[{}] {}".format(datetime.now(), msg))


def logerr(err):
    print("[{}] {}".format(datetime.now(), msg), file=sys.stderr)


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
            logerr("Exception attempting to obtain IPv6 address")
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
        logerr("Exception while requesting public IP: {}".format(e.reason))
    except Exception as e:
        logerr("Unknown exception while requesting public IP: {}".format(e))
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
                        logerr("Exception decoding JSON from DNS records: {}".format(e))
                    except KeyError as e:
                        pass
        except urllib.error.URLError as e:
            logerr("Exception while requesting DNS records: {}".format(e.reason))
        except Exception as e:
            logerr("Unknown exception while requesting DNS records: {}".format(e))
    return records


def set_dns_record(domain, token, record_id, record_type, record_data):
    url     = "https://api.digitalocean.com/v2/domains/{}/records/{}".format(domain, record_id)
    headers = { "Content-Type": "application/json", "Authorization": "Bearer {}".format(token) }
    data    = json.JSONEncoder().encode({ "data": record_data }).encode("utf-8")
    request = urllib.request.Request(url=url, headers=headers, data=data, method="PUT")
    try:
        with urllib.request.urlopen(request) as f:
            if f.status == 200 and "application/json" in f.getheader("Content-Type", ""):
                logmsg("Successfully updated {} record to {}".format(record_type, record_data))
    except urllib.error.URLError as e:
        logerr("Exception while updating {} record: {}".format(record_type, e.reason))
    except Exception as e:
        logerr("Unknown exception while updating {} record: {}".format(record_type, e))


def update_dns_record(domain, token, records, record_type):
    if record_type not in records:
        logerr("Could not locate {} record".format(record_type))
        return
    if "id" not in records[record_type]:
        logerr("Could not locate ID in {} record".format(record_type))
        return
    if "data" not in records[record_type]:
        logerr("Could not locate data in {} record".format(record_type))
        return
    ip = get_ip(record_type)
    if not ip:
        logerr("Could not get public IP for updating {} record".format(record_type))
        return
    if ip != records[record_type]["data"]:
        set_dns_record(domain, token, records[record_type]["id"], record_type, ip)
    else:
        logmsg("No IP change detected for {} record with IP {}".format(record_type, ip))


def update_dns(domain, name, token):
    logmsg("Beginning DNS update...")
    records = get_dns_records(domain, name, token)
    if records:
        update_dns_record(domain, token, records, "A")
        update_dns_record(domain, token, records, "AAAA")
    else:
        logerr("Could not retrieve domain records for {} ({})".format(domain, name))
    logmsg("OK")


if __name__ == "__main__":
    if not DO_TOKEN:
        sys.exit("DigitalOcean API token (DO_TOKEN) not specified")
    if not DO_DOMAIN:
        sys.exit("DigitalOcean domain (DO_DOMAIN) not specified")
    if not DO_NAME:
        sys.exit("DigitalOcean subdomain (DO_NAME) not specified")
    update_dns(DO_DOMAIN, DO_NAME, DO_TOKEN)
